from django.db import models
from django.contrib.auth.models import User

class JabberAccount(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    jid = models.CharField(max_length=255, unique=True)
    is_bot = models.BooleanField()

    def __unicode__(self):
        return self.jid
        
class Bot(models.Model):
    password = models.CharField(max_length=255)
    descripton = models.CharField(max_length=255)
    jid = models.ForeignKey(JabberAccount, unique=True,
                            related_name="bot_jid")
    owner = models.ManyToManyField(JabberAccount, related_name="bots")
        
    def __unicode__(self):
         return unicode(self.jid)

class InstantMessage(models.Model):
    sender = models.ForeignKey(User, editable=False)
    text = models.TextField(editable=False)
    date = models.DateTimeField(editable=False)

    def __unicode__(self):
        return '%s: %s' % (self.sender, self.text[:128])

def get_jid(jid):
    return JabberAccount.objects.get(jid=jid)