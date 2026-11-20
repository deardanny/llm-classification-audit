"""Invented records and labels: an analysis demo, not model evaluation results."""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from auditkit.analysis import paired_transitions, repeat_state
from auditkit.contracts import parse_binary
from auditkit.masking import build_school_pattern

examples = [
    {'id':1, 'text':'All students at Oak Elementary should get clearer feedback.'},
    {'id':2, 'text':'The cafeteria has blue chairs.'},
    {'id':3, 'text':'More coaching time would help.'},
]
print('SYNTHETIC DEMO — labels below are invented fixtures, not API predictions.')
masker = build_school_pattern(['ALL','Oak Elementary','All Saints School'])
print('Masking:', masker.sub('[SCHOOL]', examples[0]['text']))
control = {1:'off_topic',2:'off_topic',3:None}
treatment = {1:'on_topic',2:'off_topic',3:'on_topic'}
print(json.dumps(paired_transitions(control,treatment),indent=2))
print('Repeat disagreement:',repeat_state(['on_topic','off_topic']))
print('Validated payload:',parse_binary('{"id":1,"off_topic":false}',1,stop_reason='end_turn'))
print('A label change is an investigation target, not a verified correction.')
