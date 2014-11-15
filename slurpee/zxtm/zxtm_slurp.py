from slurpee.zxtm.objects import ZXTMState
from django.db import transaction
from settings.scrape import RETRY as MAX_RETRY

import requests

import time
import simplejson as json


class ZXTMConnector(object):
    def slurp(self):
        """Reach out to the external source"""
        retry = 0
        success = False
        # We have tried retry times
        while retry < MAX_RETRY:
            try:
                resp = self.session.get(
                    self.data_url, params=self.params, verify=self.ssl_verify
                )
            except requests.exceptions.Timeout:
                time.sleep(1)
                retry += 1
                continue

            if resp.status_code == 200:
                data = json.loads(resp.content)
                success = True
                break
            retry += 1
            print "Failed to data. Retrying...."
            time.sleep(1)

        if not success:
            raise Exception(
                "Issues connecting to {0}. Retry is {1}.".format(
                    self.data_url, MAX_RETRY
                )
            )
        return data


@transaction.commit_on_success
def slurp_zxtm_facts(source_name, source_url=None, auth=None, ssl_verify=None,
                     api_version=None):
    # Clear everything we saw last time
    zs = ZXTMState(
        filename='/home/juber/inventory/inventory/slurpee/zxtm/zxtm.json',
        version=api_version
    )

    ZXTMState.clear_orm_state()  # Deletes everything in the db
    zs.save_orm_state()
    from slurpee.zxtm.models import Node
    import pdb;pdb.set_trace()
    Node.objects.filter(node_id='10.20.77.22')
    pass

