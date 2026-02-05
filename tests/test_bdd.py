from pytest_bdd import scenarios

# from tests import smoke_steps  # noqa: F401  (важно: импорт для регистрации шагов)

scenarios("../features")
