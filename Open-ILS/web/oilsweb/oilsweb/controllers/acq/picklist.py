from oilsweb.lib.base import *
from oilsweb.lib.request import RequestMgr
import logging, pylons
import oilsweb.lib.context, oilsweb.lib.util
import oilsweb.lib.bib, oilsweb.lib.acq.search, oilsweb.lib.acq.picklist
import osrf.cache, osrf.json, osrf.ses
import oils.const, oils.utils.utils, oils.event


class PicklistController(BaseController):

    def view(self, **kwargs):
        r = RequestMgr()
        pl_manager = oilsweb.lib.acq.picklist.PicklistMgr(r, picklist_id=kwargs['id'])
        pl_manager.retrieve()
        pl_manager.retrieve_entries(flesh_provider=True, offset=r.ctx.acq.offset, limit=r.ctx.acq.limit)
        r.ctx.acq.picklist = pl_manager.picklist
        return r.render('acq/picklist/view.html')

    def view_entry(self, **kwargs):
        r = RequestMgr()
        pl_manager = oilsweb.lib.acq.picklist.PicklistMgr(r)
        entry = pl_manager.retrieve_entry(kwargs.get('id'), flesh=1, flesh_provider=True)
        pl_manager.id = entry.picklist()
        picklist = pl_manager.retrieve()
        r.ctx.acq.picklist = pl_manager.picklist
        r.ctx.acq.picklist_entry = entry
        r.ctx.acq.picklist_entry_marc_html = oilsweb.lib.bib.marc_to_html(entry.marc())
        return r.render('acq/picklist/view_entry.html')

    def list(self):
        r = RequestMgr()
        pl_manager = oilsweb.lib.acq.picklist.PicklistMgr(r)
        r.ctx.acq.picklist_list = pl_manager.retrieve_list()
        return r.render('acq/picklist/view_list.html')
         

    def search(self):
        r = RequestMgr()
        r.ctx.acq.z39_sources = oilsweb.lib.acq.search.fetch_z39_sources(r.ctx)

        sc = {}
        for data in r.ctx.acq.z39_sources.values():
            for key, val in data['attrs'].iteritems():
                sc[key] = val.get('label') or key
        r.ctx.acq.search_classes = sc
        keys = sc.keys()
        keys.sort()
        r.ctx.acq.search_classes_sorted = keys
            
        return r.render('acq/picklist/search.html')

    def do_search(self):
        r = RequestMgr()
        picklist_id = oilsweb.lib.acq.search.multi_search(
            r, oilsweb.lib.acq.search.compile_multi_search(r))
        return redirect_to(controller='acq/picklist', action='view', id=picklist_id)

    def delete(self, **kwargs):
        r = RequestMgr()
        pl_manager = oilsweb.lib.acq.picklist.PicklistMgr(r, picklist_id=kwargs['id'])
        pl_manager.delete()
        return redirect_to(controller='acq/picklist', action='list')


    def delete_entry(self, **kwargs):
        r = RequestMgr()
        pl_manager = oilsweb.lib.acq.picklist.PicklistMgr(r)
        entry_id = kwargs['id']
        entry = pl_manager.retrieve_entry(entry_id)
        pl_manager.delete_entry(entry_id)
        return redirect_to(controller='acq/picklist', action='view', id=entry.picklist())
