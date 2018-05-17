# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from __future__ import unicode_literals

from django.utils.translation import gettext_lazy as _


from django.forms import ModelForm, Textarea
from .models import Quote

from django.utils.safestring import mark_safe

class QuoteForm(ModelForm):
    
    class Meta:
        model = Quote
        fields = ['quote','last_name','for_name','nick_name','desc_author','date','header','quote_type']
        labels = {
            'quote' :  _(u'Citation ').encode('utf-8'),
            'last_name' : _(u'Nom ').encode('utf-8'),
            'for_name' : _(u'Prénom ').encode('utf-8'),
            'nick_name' : _(u'Pseudo ').encode('utf-8'),
            'desc_author' : mark_safe(_(u"Fonction, description<br/> de l'auteur/autrice ").encode('utf-8')),
            'date' : _(u'Date ').encode('utf-8'),
            'header' : _(u'En-tête ').encode('utf-8'),
            'quote_type' : _(u'Catégorie ').encode('utf-8'),
        }
        required = {
            'last_name' :  False,
            'for_name' :   False,
            'nick_name' :  False,
            'desc_author': False,
            'date' : False,
            'header' : False,
            'quote_type' : False,
        }
        widgets = {
            'quote': Textarea(attrs={'cols': 60, 'rows': 5}),
        }
