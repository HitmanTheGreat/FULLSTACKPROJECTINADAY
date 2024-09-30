import graphene
from graphene_django import DjangoObjectType
from my_app.models import Company

class CompanyType(DjangoObjectType):
  class Meta:
    model = Company
    fields = ("id", "name", "address")
    
class Query(graphene.ObjectType):
  """
  Queries for the Restaurant model
  """
  restaurants = graphene.List(CompanyType)

  def resolve_restaurants(self, info, **kwargs):
    return Company.objects.all()