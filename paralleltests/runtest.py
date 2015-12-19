from django.core.management.commands import test

from paralleltests.utils import get_env_options

args, kwargs = get_env_options

sys.exit(test.Command().execute(verbosity=1, *args, **kwargs))
