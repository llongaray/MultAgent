from multagent.integrations.git.forges import RemoteForge
class BitbucketConnector(RemoteForge):
    def __init__(self,*args,**kwargs):
        super().__init__("bitbucket",*args,**kwargs)
