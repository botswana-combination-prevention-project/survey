from faker import Faker
from model_mommy.recipe import Recipe

from .models import Survey

fake = Faker()

survey = Recipe(
    Survey,
)
