from django.contrib import admin

from .models import Election, Post, VotingSystem


class ElectionAdmin(admin.ModelAdmin):
    list_filter = ('election_type', 'voting_system')


admin.site.register(Election, ElectionAdmin)
admin.site.register(Post)
admin.site.register(VotingSystem)
