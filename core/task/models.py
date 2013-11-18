from django.db import models


class DNSIncrementalManager(models.Manager):
    def get_query_set(self):
        return super(DNSIncrementalManager, self).get_query_set().filter(ttype='dns-incremental')  # noqa


class DNSClobberManager(models.Manager):
    def get_query_set(self):
        return super(DNSClobberManager, self).get_query_set().filter(ttype='dns-clobber')  # noqa


class Task(models.Model):
    task = models.CharField(max_length=255, blank=False)
    ttype = models.CharField(max_length=255, blank=False)

    objects = models.Manager()
    dns_incremental = DNSIncrementalManager()
    dns_clobber = DNSClobberManager()

    @classmethod
    def schedule_zone_rebuild(cls, soa):
        Task(task=str(soa.pk), ttype='dns-incremental').save()

    @classmethod
    def schedule_all_dns_rebuild(cls, soa):
        Task(task=str(soa.pk), ttype='dns-clobber').save()

    def __repr__(self):
        return "<Task: {0}>".format(self)

    def __str__(self):
        return "{0} {1}".format(self.ttype, self.task)

    def save(self):
        super(Task, self).save()

    class Meta:
        db_table = u'task'
        ordering = ['task']
