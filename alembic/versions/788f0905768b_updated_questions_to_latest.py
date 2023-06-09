"""updated questions to latest

Revision ID: 788f0905768b
Revises: 3e4124da4546
Create Date: 2023-06-22 23:19:41.622654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '788f0905768b'
down_revision = '3e4124da4546'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.String(), nullable=False),
    sa.Column('mark', sa.Integer(), nullable=False),
    sa.Column('is_multi_choice', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('question_type', sa.String(), nullable=False),
    sa.Column('tolerance', sa.Float(), nullable=True),
    sa.CheckConstraint("question_type IN ('obj', 'sub_obj', 'nlp', 'maths')"),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_table('options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('option', sa.String(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_options_id'), 'options', ['id'], unique=False)
    op.create_table('scores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id', 'student_id', 'question_id', name='_assessment_student_question_uc')
    )
    op.create_index(op.f('ix_scores_id'), 'scores', ['id'], unique=False)
    op.create_table('submissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('stu_answer', sa.String(), nullable=True),
    sa.Column('stu_answer_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_index(op.f('ix_scores_id'), table_name='scores')
    op.drop_table('scores')
    op.drop_index(op.f('ix_options_id'), table_name='options')
    op.drop_table('options')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    # ### end Alembic commands ###
