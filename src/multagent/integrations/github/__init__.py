from multagent.integrations.git.forges import RemoteForge
class GitHubConnector(RemoteForge):
    def __init__(self,*args,**kwargs):super().__init__("github",*args,**kwargs)
