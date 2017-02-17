# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
from openerp.addons.survey.survey import dict_keys_startswith
from  openerp.addons import survey


class survey_inherit(models.Model):
    _inherit = 'survey.question'

    matrix_subtype = fields.Selection(selection_add=[('column_textarea', 'Column FreeText'),
                                                     ('modified_simple', 'One choice per row(modified)')])
                    
    def validate_matrix(self, cr, uid, question, post, answer_tag, context=None):
        errors = {}
        if question.constr_mandatory:
            lines_number = len(question.labels_ids_2)
            answer_candidates = dict_keys_startswith(post, answer_tag)
            print 'answer_candidates', answer_candidates
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
                
#                 answer = post[answer_tag].strip()
#                 print 'answer_number', answer
            else:
                raise RuntimeError("Invalid matrix subtype")
            # Validate that each line has been answered
            if answer_number != lines_number:
                errors.update({answer_tag: question.constr_error_msg})
        return errors
class survey_user_input_line(models.Model):
    _inherit = 'survey.user_input_line'
    
    def save_line_matrix(self, cr, uid, user_input_id, question, post, answer_tag, context=None):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        old_uil = self.search(cr, uid, [('user_input_id', '=', user_input_id),
                                        ('survey_id', '=', question.survey_id.id),
                                        ('question_id', '=', question.id)],
                              context=context)
        if old_uil:
            self.unlink(cr, SUPERUSER_ID, old_uil, context=context)

        no_answers = True
        ca = dict_keys_startswith(post, answer_tag+"_")

        comment_answer = ca.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update({'answer_type': 'text', 'value_text': comment_answer})
            self.create(cr, uid, vals, context=context)
            no_answers = False

        if question.matrix_subtype == 'simple':
            for row in question.labels_ids_2:
                a_tag = "%s_%s" % (answer_tag, row.id)
                if a_tag in ca:
                    no_answers = False
                    vals.update({'answer_type': 'suggestion', 'value_suggested': ca[a_tag], 'value_suggested_row': row.id})
                    self.create(cr, uid, vals, context=context)

        elif question.matrix_subtype == 'multiple':
            for col in question.labels_ids:
                for row in question.labels_ids_2:
                    a_tag = "%s_%s_%s" % (answer_tag, row.id, col.id)
                    if a_tag in ca:
                        no_answers = False
                        vals.update({'answer_type': 'suggestion', 'value_suggested': col.id, 'value_suggested_row': row.id})
                        self.create(cr, uid, vals, context=context)
                        
        elif question.matrix_subtype == 'column_textarea':
            print 'column_textarea'
            for col in question.labels_ids:
                for row in question.labels_ids_2:
                    a_tag = "%s_%s_%s" % (answer_tag, row.id, col.id)
                    if a_tag in ca:
                        no_answers = False
                        vals.update({'answer_type': 'free_text', 'value_suggested': col.id, 'value_suggested_row': row.id, 'value_free_text':ca[a_tag]})
                        self.create(cr, uid, vals, context=context)
        
        if no_answers:
            vals.update({'answer_type': None, 'skipped': True})
            self.create(cr, uid, vals, context=context)
        return True



