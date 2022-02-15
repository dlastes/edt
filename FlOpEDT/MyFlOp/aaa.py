C=Course.objects.filter(module__abbrev='r101')
for w in C.distinct('week'):
    Cw = C.filter(week=w.week)
    D=Dependency.objects.filter(course1__in=Cw, course2__type__name='TP_2_5')
    for d in D:
        TP=d.course2
        TD=Course.objects.get(module=TP.module, type__name='TD_1',groups=TP.groups.first(), week=TP.week)
        d.course1=TD


liste_de_C = [Course.objects.filter(module__abbrev='r106', type__name='TD_1_5', type__department__abbrev='V2'),
Course.objects.filter(module__abbrev='r107', type__name='TD_1_5', type__department__abbrev='V2'),
Course.objects.filter(module__abbrev='m3201', type__name='TD_1', type__department__abbrev='V2'),
Course.objects.filter(module__abbrev='am3201', type__name='TD_1_5', type__department__abbrev='V2'),
Course.objects.filter(module__abbrev='m3202', type__name='TD_1_25', type__department__abbrev='V2'),
Course.objects.filter(module__abbrev='am3202', type__name='TD_2_5', type__department__abbrev='V2')]
for C in liste_de_C:
    for c in C:
        tps=Course.objects.filter(module=c.module,groups__in=c.groups.first().descendants_groups(), week=c.week)
        P,created=Pivot.objects.get_or_create(pivot_course=c, ND=True)
        for tp in tps:
            P.other_courses.add(tp)