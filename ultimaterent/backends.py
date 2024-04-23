from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Agent

User = get_user_model()


class AgentAuthBackend(BaseBackend):
    def authenticate(self, request, agent_id=None):
        try:
            agent = Agent.objects.get(agent_id=agent_id)
            return agent.user  # Return the associated User object
        except Agent.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
