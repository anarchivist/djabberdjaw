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

# TODO: provide threading for multiple bots

import re
from datetime import datetime

from PyZ3950 import zoom
import pymarc
from jabberbot import JabberBot

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from worldcat.request.xid import xISBNRequest

from djabberdjaw.bot.models import Bot, JabberAccount, get_jid, InstantMessage

ZSERVER = {'host': 'z3950.loc.gov', 'port': 7090, 'db': 'VOYAGER',
          'qsyntax': 'CCL', 'rsyntax': 'USMARC', 'element_set': 'F'}

def jl(l):
    return ', '.join(l)

class LabsBot(JabberBot):
    def callback_message(self, conn, mess):
        sender = mess.getFrom().getStripped()
        if sender not in self.jids():
            u = User(id=None, username=sender)
            u.save()
            j = JabberAccount(user=User.objects.get(username=sender),
                id=None, is_bot=False, jid=sender)
            j.save()
        a = InstantMessage(id=None,
                        sender=User.objects.get(jabberaccount__jid=sender), 
                        text=mess.getBody(), date=datetime.now())
        a.save()
        super(LabsBot, self).callback_message(conn, mess)
        # else:
        #     return "%s is not registered; ignoring command" % mess.getFrom()
    
    def send(self, user, text, in_reply_to = None):
        a = InstantMessage(id=None, 
                            sender=User.objects.get(username=\
                            self.get_username(self.jid.getStripped())),
                            text=text, date=datetime.now())
        a.save()
        super(LabsBot, self).send(user, text, in_reply_to)
        
    def jids(self):
        return [x.jid for x in JabberAccount.objects.all()]
        
    def owners(self):
        _ = Bot.objects.get(jid=get_jid(self.jid.getStripped()))
        return [o.jid for o in _.owner.all()]
        
    def users(self):
        return [u.username for u in User.objects.all()]
    
    def lookup_sender(self, mess):
        jid = mess.getFrom().getStripped()
        try:
            sender = User.objects.get(jabberaccount__jid=jid).username
        except django.contrib.auth.models.DoesNotExist:
            sender = jid
        return jid

    def get_username(self, jid):
        return User.objects.get(jabberaccount__jid=jid).username

    def get_user_jid(self, u, bot=True):
        return [j.jid for j in JabberAccount.objects.filter(user__username=u)]
    
    def bot_all(self, mess, args):
        """(all <msg>): Send a message to all registered users"""
        sender = self.lookup_sender(mess)
        users = self.users()
        recipients = []
        if len(users):
            for user in users:
                recipients.extend(self.get_user_jid(user))
            for recipient in recipients:
                self.send(recipient, '%s said to all: %s' % (sender, args))

    def bot_lookup(self, mess, args):
        """(lookup <user>): List a user's Jabber accounts"""
        return 'User %s associated with XMPP accounts: %s' % \
                (args, jl(self.get_user_jid(args)))

    def bot_owners(self, mess, args):
        """List this bot's owners"""
        return 'Owners: %s' % jl(set(map(self.get_username, self.owners())))
        
    def bot_tell(self, mess, args):
        """(tell <user> <msg>): Send a message to another user privately"""
        sender = self.lookup_sender(mess)
        recipient = args.split()[0]
        msg = " ".join(args.split()[1:])
        for u in self.get_user_jid(recipient):
            self.send(u, '%s said: %s' % (sender, msg))

    # def bot_test(self, mess, args):
    #     return mess.__dict__
    
    def bot_users(self, mess, args):
        """List known users of this bot"""
        return "Known users: %s" % jl(self.users())
    
    def bot_whoami(self, mess, args):
        """Show your associated username"""
        return 'You are %s' % self.get_username(self.lookup_sender(mess))
    
    def bot_xisbn_get_editions(self, mess, args):
        """(xisbn_get_editions <isbn>): Get other editions for a work"""
        xisbn = xISBNRequest(method='getEditions', rec_num=args, fl="year")
        return repr(xisbn.get_response().data['list'])
    
    def bot_xisbn_get_metadata(self, mess, args):
        """(xisbn_get_metadata <isbn>): Retrieve metadata for a given ISBN"""
        xisbn = xISBNRequest(method='getMetadata', rec_num=args)
        r = xisbn.get_response().data['list'][0]
        out = '%s %s. %s : %s, %s' % (r['title'], r['author'], r['city'],
                                        r['publisher'], r['year'])
        return out
        
    def bot_zinfo(self, mess, args):
        """Show info about the server used for zsearch"""
        return repr(ZSERVER)
    
    def bot_zsearch(self, mess, args):
        """(zsearch <query>): Search a remote Z39.50 target"""
        conn = zoom.Connection(ZSERVER['host'], ZSERVER['port'],
                                 databaseName=ZSERVER['db'],
                                 preferredRecordSyntax=ZSERVER['rsyntax'],
                                 elementSetName=ZSERVER['element_set'])
        query = zoom.Query(ZSERVER['qsyntax'], args)
        result_set = conn.search(query)
        results = [pymarc.map_marc8_record(pymarc.Record(data=r.data))
                    for r in result_set]
        if len(results) >= 10: results = results[:10]
        out = []
        c = 1
        for r in results:
            out.append('%s: %s %s' % (c, r.author(), r.title()))
            c += 1
        conn.close()
        return "\n".join(out)

class Command(BaseCommand):
    help = "Start the djabberdjaw XMPP bot"
    def handle(self, *args, **options):
        b = Bot.objects.all()[0]
        bot = LabsBot(b.jid.jid, b.password)
        bot.serve_forever()