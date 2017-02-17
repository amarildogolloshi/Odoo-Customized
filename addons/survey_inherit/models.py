# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.addons.survey.survey import dict_keys_startswith

class survey_inherit(models.Model):
    _inherit = 'survey.question'

    matrix_subtype = fields.Selection(selection_add=[('column_textarea', 'Column FreeText'),
                                                     ('modified_simple', 'One choice per row(modified)')])
                    
    def validate_matrix(self, cr, uid, question, post, answer_tag, context=None):
        errors = {}
        if question.constr_mandatory:
            lines_number = len(question.labels_ids_2)
            answer_candidates = dict_keys_startswith(post, answer_tag)
            comment_answer = answer_candidates.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
            # Number of lines that have been answered
            if question.matrix_subtype == 'simple':
                answer_number = len(answer_candidates)
            elif question.matrix_subtype == 'multiple':
                answer_number = len(set([sk.rsplit('_', 1)[0] for sk in answer_candidates.keys()]))
            elif question.matrix_subtype == 'modified_simple':
                answer_number = len(answer_candidates)
            elif question.matrix_subtype == 'column_textarea':
                answer_number = len(set([sk.rsplit('_', 1)[0] for sk in answer_candidates.keys()]))
            else:
                raise RuntimeError("Invalid matrix subtype")
            # Validate that each line has been answered
            if answer_number != lines_number:
                errors.update({answer_tag: question.constr_error_msg})
        return errors
