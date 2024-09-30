import graphene
from graphene_django import DjangoObjectType
from my_app.models import Company
from graphql_auth.schema import MeQuery, UserQuery
from graphql_auth import mutations
from graphql import GraphQLError

class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = ("id", "name", "address")


class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        address = graphene.String(required=True)

    ok = graphene.Boolean()
    company = graphene.Field(CompanyType)

    def mutate(self, info, name, address):
        if not info.context.user.is_authenticated:
            raise GraphQLError("User is not authenticated.")
        if not info.context.user.has_perm('my_app.add_company'): 
            raise GraphQLError("User does not have permission to add a company.")
        
        company = Company(name=name, address=address)
        company.save()
        return CreateCompany(ok=True, company=company)


class DeleteCompany(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    msg = graphene.String()

    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError("User is not authenticated.")
        if not info.context.user.has_perm('my_app.delete_company'): 
            raise GraphQLError("User does not have permission to delete a company.")
        
        try:
            company = Company.objects.get(id=id)
            company.delete()
            return DeleteCompany(msg="Company deleted successfully.")
        except Company.DoesNotExist:
            raise GraphQLError("Company not found.")


class UpdateCompany(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        address = graphene.String(required=True)

    ok = graphene.Boolean()
    company = graphene.Field(CompanyType)

    def mutate(self, info, id, name, address):
        if not info.context.user.is_authenticated:
            raise GraphQLError("User is not authenticated.")
        if not info.context.user.has_perm('my_app.change_company'): 
            raise GraphQLError("User does not have permission to update a company.")


        try:
            company = Company.objects.get(id=id)
            company.name = name
            company.address = address
            company.save()
            return UpdateCompany(ok=True, company=company)
        except Company.DoesNotExist:
            raise GraphQLError("Company not found.")

class Query(UserQuery, MeQuery ,graphene.ObjectType):
    
    companies = graphene.List(CompanyType)
    get_company_by_id = graphene.Field(CompanyType, id=graphene.Int(required=True))

    def resolve_companies(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError("User is not authenticated.")
        
        if not info.context.user.has_perm('my_app.view_company'):
            raise GraphQLError("You do not have permission to view companies.")
        
        return Company.objects.all()

    def resolve_get_company_by_id(self, info, id):
        if not info.context.user.is_authenticated:
            raise GraphQLError("User is not authenticated.")

        if not info.context.user.has_perm('my_app.view_company'):
            raise GraphQLError("You do not have permission to view this company.")
        
        try:
            return Company.objects.get(id=id)
        except Company.DoesNotExist:
            raise GraphQLError("Company not found.")


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_change = mutations.PasswordChange.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    update_account = mutations.UpdateAccount.Field()
    send_secondary_email_activation = mutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    swap_emails = mutations.SwapEmails.Field()

    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()
    
class Mutation(AuthMutation,graphene.ObjectType):
    create_company = CreateCompany.Field()
    delete_company = DeleteCompany.Field()
    update_company = UpdateCompany.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
