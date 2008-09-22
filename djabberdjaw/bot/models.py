# Copyright (C) 2008 Mark A. Matienzo
# 
# This file is part of djabberdjaw.
# 
# djabberdjaw is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# djabberdjaw is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with djabberdjaw.  If not, see <http://www.gnu.org/licenses/>.

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