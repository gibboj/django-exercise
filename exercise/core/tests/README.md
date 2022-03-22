# Recipe Django Exercise

## Summary
Create a CRUD app for recipes, that allows adding/deleting recipes. Have tests for all actions

## Models
Recipe
* name
* description

Ingredients
* name
* recipe (foreginKey to point to model)

# GET
/recipe
: Return all recipes as a list, with ingredients attached

/recipe/<RECIPE_ID>
: Return one recipe with ingredients attached

/recipe/?name=<FRAGMENT>
:Filter recipe by name, return list


# PATCH
