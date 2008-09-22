from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms

from djabberdjaw.bot.models import Bot, JabberAccount, InstantMessage


_jid = lambda x : x.jid
_owner = lambda x : x.owner.all()

class BotAdminForm(forms.ModelForm):
    """docstring for BotAdminForm"""
        
    class Meta:
        model = Bot

    # __q = JabberAccount.objects.exclude(jid__in=map(_jid, map(_jid, __bots)))
    # #jid = forms.ModelChoiceField()
    # owner = forms.ModelMultipleChoiceField(queryset=__q)
    
    password = forms.CharField(widget=forms.PasswordInput)

    

    def clean(self):
        __bots = map(_jid, Bot.objects.all())
        bot = self.data.get('jid')
        bot_jid = self.cleaned_data.get('jid')
        o = self.data.get('owner')
        #raise repr(self.__dict__)
        if bot_jid.is_bot == False:
            raise forms.ValidationError('Jabber account must be flagged as bot')
        if (bot in o):
            raise forms.ValidationError('Bot cannot own itself')
        if (len(__bots) > 1) and (bot_jid in __bots):
            raise forms.ValidationError('Bot cannot be owned by another bot')
        return super(BotAdminForm, self).clean()

    
    # def clean(self, *args, **kwargs):
    #     raise forms.ValidationError ('try')
    #     self.clean_jid()
    #     return super(BotAdminForm, self).clean(*args, **kwargs)
        
class BotAdmin(admin.ModelAdmin):
    form = BotAdminForm
    list_display = ('jid', 'descripton')
    #fields = ('bot_jid', 'password', 'description', 'owner')

class InstantMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text', 'date')
    date_hierarchy = 'date'

class UserJIDInline(admin.TabularInline):
    model = JabberAccount

class UserJIDAdmin(UserAdmin):
    inlines = [UserJIDInline]

admin.site.register(InstantMessage, InstantMessageAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.unregister(User)
admin.site.register(User, UserJIDAdmin)


