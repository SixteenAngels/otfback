"""Initial migration creating all tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Define enum types
def upgrade():
    """Create all tables with new schema."""
    # Create enum types
    user_role_enum = postgresql.ENUM('admin', 'scanner', 'viewer', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    ticket_status_enum = postgresql.ENUM(
        'created', 'sold', 'scanned_entry', 'attended', 'refunded', 'transferred',
        name='ticketstatus'
    )
    ticket_status_enum.create(op.get_bind(), checkfirst=True)
    
    scan_type_enum = postgresql.ENUM(
        'sale_confirmation', 'entry_check', 'attendance',
        name='scantype'
    )
    scan_type_enum.create(op.get_bind(), checkfirst=True)
    
    refund_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'completed',
        name='refundstatus'
    )
    refund_status_enum.create(op.get_bind(), checkfirst=True)
    
    transfer_status_enum = postgresql.ENUM(
        'pending', 'accepted', 'rejected', 'completed',
        name='transferstatus'
    )
    transfer_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create concerts table
    op.create_table(
        'concerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('venue', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_concerts_id'), 'concerts', ['id'], unique=False)
    op.create_index(op.f('ix_concerts_name'), 'concerts', ['name'], unique=False)
    
    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('concert_id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(), nullable=False),
        sa.Column('qr_code_data', sa.String(), nullable=False),
        sa.Column('status', ticket_status_enum, nullable=False),
        sa.Column('buyer_name', sa.String(), nullable=True),
        sa.Column('buyer_email', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.Column('original_buyer_id', sa.Integer(), nullable=True),
        sa.Column('current_holder_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['concert_id'], ['concerts.id']),
        sa.ForeignKeyConstraint(['original_buyer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['current_holder_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_number'),
    )
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=False)
    op.create_index(op.f('ix_tickets_concert_id'), 'tickets', ['concert_id'], unique=False)
    op.create_index(op.f('ix_tickets_ticket_number'), 'tickets', ['ticket_number'], unique=False)
    
    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('scan_type', scan_type_enum, nullable=False),
        sa.Column('scanned_at', sa.DateTime(), nullable=False),
        sa.Column('scanned_by_user_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id']),
        sa.ForeignKeyConstraint(['scanned_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_scans_id'), 'scans', ['id'], unique=False)
    op.create_index(op.f('ix_scans_ticket_id'), 'scans', ['ticket_id'], unique=False)
    
    # Create refunds table
    op.create_table(
        'refunds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', refund_status_enum, nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('requested_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_refunds_id'), 'refunds', ['id'], unique=False)
    op.create_index(op.f('ix_refunds_ticket_id'), 'refunds', ['ticket_id'], unique=False)
    
    # Create transfers table
    op.create_table(
        'transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('from_user_id', sa.Integer(), nullable=False),
        sa.Column('to_user_id', sa.Integer(), nullable=False),
        sa.Column('status', transfer_status_enum, nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('initiated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id']),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_transfers_id'), 'transfers', ['id'], unique=False)
    op.create_index(op.f('ix_transfers_ticket_id'), 'transfers', ['ticket_id'], unique=False)


def downgrade():
    """Drop all tables."""
    op.drop_table('transfers')
    op.drop_table('refunds')
    op.drop_table('scans')
    op.drop_table('tickets')
    op.drop_table('concerts')
    op.drop_table('users')
    
    # Drop enum types
    postgresql.ENUM(name='transferstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='refundstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='scantype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='ticketstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='userrole').drop(op.get_bind(), checkfirst=True)
