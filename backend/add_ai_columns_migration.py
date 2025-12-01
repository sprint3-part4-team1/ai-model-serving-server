"""
Add is_ai_generated_image and is_ai_generated_description columns to menu_items table
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.logging import app_logger as logger


def migrate():
    """Add new columns to menu_items table"""
    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check if columns already exist
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='menu_items'
                AND column_name IN ('is_ai_generated_image', 'is_ai_generated_description')
            """)

            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]

            if 'is_ai_generated_image' in existing_columns and 'is_ai_generated_description' in existing_columns:
                logger.info("Columns already exist. No migration needed.")
                print("Columns already exist. No migration needed.")
                return

            # Add is_ai_generated_image column
            if 'is_ai_generated_image' not in existing_columns:
                logger.info("Adding is_ai_generated_image column...")
                print("Adding is_ai_generated_image column...")
                conn.execute(text("""
                    ALTER TABLE menu_items
                    ADD COLUMN is_ai_generated_image BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                logger.info("is_ai_generated_image column added")
                print("is_ai_generated_image column added")

            # Add is_ai_generated_description column
            if 'is_ai_generated_description' not in existing_columns:
                logger.info("Adding is_ai_generated_description column...")
                print("Adding is_ai_generated_description column...")
                conn.execute(text("""
                    ALTER TABLE menu_items
                    ADD COLUMN is_ai_generated_description BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                logger.info("is_ai_generated_description column added")
                print("is_ai_generated_description column added")

            print("\nMigration completed successfully!")
            logger.info("Migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"Migration failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    migrate()
