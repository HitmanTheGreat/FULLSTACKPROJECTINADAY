import graphene
from graphene_django import DjangoObjectType
from my_app.models import Company
from graphql_auth.schema import MeQuery, UserQuery
from graphql_auth import mutations

    
class CompanyType(DjangoObjectType):
  class Meta:
    model = Company
    fields = ("id", "name", "address")
    
    
class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        address = graphene.String()
        
    ok = graphene.Boolean() 
    company = graphene.Field(CompanyType)

    def mutate(self, info, name, address):
        company = Company(name=name, address=address)
        company.save()
        return CreateCompany(ok=True, company=company)
    
    
class DeleteCompany(graphene.Mutation):
  class Arguments:
    id = graphene.Int()

  msg = graphene.String()
  
  def mutate(self, info, id):
    restaurant = Company.objects.get(id=id)
    restaurant.delete()
    return DeleteCompany(msg = "Company deleted Successfully")

class UpdateCompany(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    name = graphene.String()
    address = graphene.String()

  ok = graphene.Boolean()
  company = graphene.Field(CompanyType)

  def mutate(self, info, id, name, address):
    company = Company.objects.get(id=id)
    company.name = name
    company.address = address
    company.save()
    return UpdateCompany(ok=True, company=company)

class Query(UserQuery, MeQuery ,graphene.ObjectType):
    
    companies = graphene.List(CompanyType)
    get_company_by_id = graphene.Field(CompanyType, id=graphene.Int(required=True))

    def resolve_companies(self, info, **kwargs):
        return Company.objects.all()

    def resolve_get_company_by_id(self, info, id):
        try:
            return Company.objects.get(id=id)
        except Company.DoesNotExist:
            return None

    
class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    delete_company = DeleteCompany.Field()
    update_company = UpdateCompany.Field()

    user_registration = mutations.Register.Field()
    user_verification = mutations.VerifyAccount.Field()
    user_authentication = mutations.ObtainJSONWebToken.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
