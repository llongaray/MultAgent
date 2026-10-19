from multagent.integrations.git.forges import RemoteForge
class GitLabConnector(RemoteForge):
    def __init__(self,*args,**kwargs):super().__init__("gitlab",*args,**kwargs)
