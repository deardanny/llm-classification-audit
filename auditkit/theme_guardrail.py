"""Retain verified difficulty themes and withhold unsupported themes individually.

This routes existing verifier judgments. It does not call a model, reinterpret
negative predictions, or turn an unverified positive into a negative.
"""
from copy import deepcopy
from collections.abc import Mapping
import re

from .evidence import quote_present

VERSION='theme-routing-v1'


def theme_id(value):
    if type(value)is int and 1<=value<=24:return value
    if isinstance(value,str) and re.fullmatch(r'[1-9][0-9]*',value) and 1<=int(value)<=24:return int(value)
    raise ValueError('Invalid theme identifier')


def normalized_map(value):
    if not isinstance(value,Mapping):raise ValueError('Expected theme mapping')
    result={}
    for key,item in value.items():
        tid=theme_id(key)
        if tid in result:raise ValueError('Duplicate normalized theme identifier')
        result[tid]=item
    return result


def held_result(reason,held=None):
    return {'action':'hold','label':None,'accepted_themes':{},'held_themes':held or {},
            'requires_review':True,'reason':reason}


def route(comment,prediction,verdicts=None):
    if not isinstance(comment,str) or not comment.strip():return held_result('invalid_comment')
    if not isinstance(prediction,Mapping):return held_result('missing_or_invalid_prediction')
    status=prediction.get('status')
    if type(status)is not int or status not in (0,1,2):return held_result('invalid_prediction_status')
    if status==2:return held_result('unclear_prediction')
    try:proposed=normalized_map(prediction.get('themes',{}))
    except ValueError:return held_result('invalid_proposed_theme_identifiers')
    if status==0:
        if proposed:return held_result('status_theme_conflict')
        return {'action':'auto_accept','label':0,'accepted_themes':{},'held_themes':{},
                'requires_review':False,'reason':'no_difficulty_claim_to_gate'}
    if not proposed:return held_result('missing_themes')
    def all_held(reason):return held_result(reason,{t:{'reason':reason} for t in proposed})
    if verdicts is None:return all_held('missing_or_invalid_verifier')
    try:checked=normalized_map(verdicts)
    except ValueError:return all_held('invalid_verifier_identifiers')
    if not set(checked)<=set(proposed):return all_held('unexpected_verifier_theme')
    evidence=prediction.get('evidence',[])
    if not isinstance(evidence,list):return all_held('invalid_proposal_evidence')
    source_quotes={};duplicates=set()
    for item in evidence:
        if not isinstance(item,Mapping):return all_held('invalid_proposal_evidence')
        try:tid=theme_id(item.get('theme_id'))
        except ValueError:return all_held('invalid_evidence_identifier')
        if tid not in proposed:return all_held('unexpected_evidence_theme')
        if tid in source_quotes:duplicates.add(tid)
        source_quotes[tid]=item.get('quote')
    accepted={};held={}
    for tid,spans in proposed.items():
        verdict=checked.get(tid)
        if tid in duplicates:reason='duplicate_proposal_evidence'
        elif not quote_present(source_quotes.get(tid),comment):reason='proposal_quote_missing'
        elif not isinstance(verdict,Mapping):reason='missing_or_invalid_theme_verdict'
        elif verdict.get('verdict') not in ('explicit','not_explicit','unclear'):reason='invalid_theme_verdict'
        elif verdict.get('verdict')!='explicit':reason='theme_not_explicitly_supported'
        elif not quote_present(verdict.get('quote'),comment):reason='verifier_quote_missing'
        else:reason=None
        if reason:
            held[tid]={'reason':reason,'verifier_verdict':verdict.get('verdict') if isinstance(verdict,Mapping) else None}
        else:
            accepted[tid]={'source_spans':deepcopy(spans),'proposal_quote':source_quotes[tid],
                           'verified_quote':verdict['quote'],'verifier_verdict':'explicit'}
    if not accepted:return held_result('no_supported_theme',held)
    return {'action':'partial_accept' if held else 'auto_accept','label':1,
            'accepted_themes':accepted,'held_themes':held,'requires_review':bool(held),
            'reason':'supported_themes_retained_others_held' if held else 'all_proposed_themes_supported'}
