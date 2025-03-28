"""
Custom Flask CLI commands for Ad Automation P-01 project.
"""
import click
import os
import sys
import json
from sqlalchemy import text
from flask.cli import with_appcontext
import random
from app import db
from app.models.job_opening import JobOpening
from app.models.candidate import Candidate
from app.models.ad_campaign import SocialMediaPlatform, AdCampaign

# Add parent directory to path so we can import from ml/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def register_commands(app):
    """Register custom CLI commands."""
    
    @app.cli.group()
    def data():
        """Data-related commands."""
        pass
    
    @data.command()
    @click.option('--candidates', default=100, help='Number of candidates to generate')
    @click.option('--jobs', default=20, help='Number of job openings to generate')
    def generate(candidates, jobs):
        """Generate simulated data."""
        try:
            from ml.data_generator import DataGenerator
            
            generator = DataGenerator()
            
            # Generate data
            candidates_df = generator.generate_candidates(candidates)
            job_openings_df = generator.generate_job_openings(jobs)
            platforms_df = generator.generate_social_media_platforms()
            
            # Create data directory if it doesn't exist
            os.makedirs('ml/data', exist_ok=True)
            
            # Save to CSV
            candidates_df.to_csv('ml/data/candidates.csv', index=False)
            job_openings_df.to_csv('ml/data/job_openings.csv', index=False)
            platforms_df.to_csv('ml/data/platforms.csv', index=False)
            
            click.echo(f"Generated {len(candidates_df)} candidates")
            click.echo(f"Generated {len(job_openings_df)} job openings")
            click.echo(f"Generated {len(platforms_df)} social media platforms")
            click.echo(f"Data saved to CSV files in ml/data/")
            
            # Insert data into the database
            generator.insert_candidates_to_db(candidates_df)
            generator.insert_job_openings_to_db(job_openings_df)
            generator.insert_platforms_to_db(platforms_df)
            
        except Exception as e:
            click.echo(f"Error generating data: {str(e)}", err=True)
    
    @data.command()
    @click.option('--limit', default=None, type=int, help='Limit number of candidates to cluster')
    @click.option('--clusters', default=5, help='Number of clusters to create')
    @click.option('--find-optimal', is_flag=True, help='Find optimal number of clusters')
    def cluster(limit, clusters, find_optimal):
        """Run clustering on candidates."""
        try:
            from ml.clustering import CandidateClusteringModel
            
            # Load candidate data
            candidates_df = CandidateClusteringModel.load_candidates_from_db()
            
            if candidates_df is None or len(candidates_df) == 0:
                click.echo("No candidate data available. Please generate data first.", err=True)
                return
            
            if limit and limit < len(candidates_df):
                candidates_df = candidates_df.sample(limit)
                click.echo(f"Using {limit} random candidates for clustering")
            
            # Initialize and train the model
            model = CandidateClusteringModel(n_clusters=clusters)
            model.train(candidates_df, find_optimal=find_optimal)
            
            # Predict clusters
            clusters = model.predict(candidates_df)
            
            # Get cluster characteristics
            characteristics = model.get_cluster_characteristics(candidates_df, clusters)
            
            # Print characteristics
            for cluster_id, chars in characteristics.items():
                click.echo(f"\nCluster {cluster_id} ({chars['size']} candidates):")
                click.echo(f"Average age: {chars['avg_age']:.1f}")
                click.echo(f"Average experience: {chars['avg_experience']:.1f} years")
                click.echo(f"Average desired salary: ${chars['avg_salary']:,.2f}")
                
                click.echo("\nTop education levels:")
                for edu, pct in sorted(chars['education_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]:
                    click.echo(f"  - {edu}: {pct*100:.1f}%")
                
                click.echo("\nTop desired industries:")
                for ind, pct in sorted(chars['industry_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]:
                    click.echo(f"  - {ind}: {pct*100:.1f}%")
            
            # Update segments in the database
            model.update_candidate_segments(candidates_df)
            
            click.echo("\nCandidate segmentation completed successfully!")
            
        except Exception as e:
            click.echo(f"Error clustering candidates: {str(e)}", err=True)
    
    @data.command()
    @click.option('--visualize', is_flag=True, help='Generate visualization of clusters')
    @click.option('--clusters', default=5, help='Number of clusters for segmentation')
    def segment(visualize, clusters):
        """Train the audience segmentation model for targeted advertising."""
        try:
            # Add project root to path
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if project_root not in sys.path:
                sys.path.append(project_root)
            
            click.echo("Starting audience segmentation model training...")
            
            # Import at runtime to avoid circular imports
            from ml.train_model import main as train_model_main
            
            # Run the training script with options
            train_model_main(n_clusters=clusters, visualize=visualize)
            
            click.echo("\nAudience segmentation model trained successfully!")
            click.echo("Model saved to ml/models/segment_model.joblib")
            click.echo("Cluster descriptions saved to ml/models/cluster_descriptions.json")
            
            if visualize:
                click.echo("Visualization saved to ml/models/segment_visualization.png")
            
            # Inform about integrating with campaigns
            click.echo("\nTo use these segments in campaigns, use the CampaignManager.create_audience_segments() method")
            click.echo("or access the API endpoint at /api/segmentation/segments/create")
            
        except Exception as e:
            click.echo(f"Error training segmentation model: {str(e)}", err=True)
    
    @app.cli.group()
    def db():
        """Database management commands."""
        pass
    
    @db.command()
    def setup():
        """Initialize the database with required tables."""
        from app import db
        
        try:
            db.create_all()
            click.echo("Database tables created successfully")
        except Exception as e:
            click.echo(f"Error creating database tables: {str(e)}", err=True)
    
    @db.command()
    def reset():
        """Reset the database by dropping and recreating all tables."""
        from app import db
        
        try:
            db.drop_all()
            db.create_all()
            click.echo("Database has been reset successfully")
        except Exception as e:
            click.echo(f"Error resetting database: {str(e)}", err=True)
    
    @db.command()
    def status():
        """Check the status of the database."""
        from app import db
        
        try:
            # Execute a simple query to check if database is available
            result = db.session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                click.echo("Database connection is healthy")
                
                # Count records in each table
                tables = {
                    'job_openings': db.session.execute(text("SELECT COUNT(*) FROM job_openings")).scalar(),
                    'candidates': db.session.execute(text("SELECT COUNT(*) FROM candidates")).scalar(),
                    'social_media_platforms': db.session.execute(text("SELECT COUNT(*) FROM social_media_platforms")).scalar(),
                    'ad_campaigns': db.session.execute(text("SELECT COUNT(*) FROM ad_campaigns")).scalar()
                }
                
                click.echo("\nRecord counts:")
                for table, count in tables.items():
                    click.echo(f"  - {table}: {count} records")
                
                # Check candidate segments
                segments = db.session.execute(text(
                    "SELECT segment_id, COUNT(*) FROM candidates WHERE segment_id IS NOT NULL GROUP BY segment_id"
                )).fetchall()
                
                if segments:
                    click.echo("\nCandidate segments:")
                    for segment_id, count in segments:
                        click.echo(f"  - Segment {segment_id}: {count} candidates")
                else:
                    click.echo("\nNo candidate segments have been created yet")
                
            else:
                click.echo("Database connection failed", err=True)
        except Exception as e:
            click.echo(f"Error checking database status: {str(e)}", err=True) 
    
    @app.cli.group()
    def credentials():
        """Manage API credentials."""
        pass
    
    @credentials.command('list')
    def list_credentials():
        """List all configured credentials."""
        from app.utils.credentials import credential_manager
        
        for platform in ['META', 'GOOGLE', 'TWITTER']:
            creds = credential_manager.get_credentials(platform)
            click.echo(f"\n{platform} Credentials:")
            if not creds:
                click.echo("  Not configured")
                continue
                
            for key, value in creds.items():
                masked = credential_manager.mask_value(value)
                click.echo(f"  {key}: {masked}")
    
    @credentials.command('health')
    def health_check():
        """Check the health of all credentials."""
        from app.utils.key_rotation import check_credentials_validity
        from app.utils.api_debug import test_api_connections
        
        health = check_credentials_validity()
        
        click.echo("\nCredential Health Check:")
        for platform, platform_health in health.items():
            if platform == 'expiring_keys':
                continue
                
            click.echo(f"\n{platform}:")
            if platform_health.get('valid'):
                click.echo(f"  Status: ✅ Valid")
                expiration = platform_health.get('expiration')
                days = platform_health.get('days_remaining')
                if expiration:
                    click.echo(f"  Expires: {expiration}")
                    if days and days < 30:
                        click.echo(f"  WARNING: Expires in {days} days")
                else:
                    click.echo("  No expiration")
            else:
                click.echo(f"  Status: ❌ Invalid")
                click.echo(f"  Error: {platform_health.get('error', 'Unknown error')}")
        
        # Show expiring keys
        expiring_keys = health.get('expiring_keys', {})
        if expiring_keys:
            click.echo("\nExpiring Keys:")
            for key, data in expiring_keys.items():
                click.echo(f"  {key}: Expires in {data.get('days_remaining')} days")
        
        # Connection tests
        click.echo("\nTesting API Connections:")
        test_results = test_api_connections()
        for platform, result in test_results.items():
            if result.get('success'):
                click.echo(f"  {platform}: ✅ Connected")
            else:
                click.echo(f"  {platform}: ❌ Failed")
                click.echo(f"    Error: {result.get('message', 'Unknown error')}")
    
    @credentials.command('rotate')
    @click.argument('platform')
    @click.argument('key')
    def rotate_credential(platform, key):
        """Rotate a specific credential."""
        from app.utils.key_rotation import rotate_meta_token
        
        if platform != 'META' or key != 'META_ACCESS_TOKEN':
            click.echo("❌ Only META_ACCESS_TOKEN rotation is currently supported")
            return 1
            
        click.echo(f"Rotating {platform}/{key}...")
        result = rotate_meta_token()
        
        if result.get('success'):
            click.echo(f"✅ {platform}/{key} rotated successfully")
            if 'expires_in' in result:
                seconds = result['expires_in']
                days = seconds // 86400
                click.echo(f"New token expires in {days} days")
        else:
            click.echo(f"❌ Error rotating {platform}/{key}: {result.get('error', 'Unknown error')}")
            return 1
    
    @credentials.command('export')
    @click.argument('filename', default='.env.exported')
    def export_credentials(filename):
        """Export credentials to a file."""
        from app.utils.credentials import credential_manager
        
        click.echo(f"Exporting credentials to {filename}...")
        result = credential_manager.export_to_env_file(filename)
        
        if result:
            click.echo(f"✅ Credentials exported to {filename}")
        else:
            click.echo(f"❌ Error exporting credentials")
            return 1
    
    @app.cli.group()
    def config():
        """Manage application configuration."""
        pass
    
    @config.command('show')
    def show_config():
        """Show current application configuration."""
        from app.utils.config import config_manager
        from app.utils.credentials import credential_manager
        
        config = config_manager.get_all()
        
        click.echo("\nApplication Configuration:")
        click.echo(f"Environment: {config.get('ENVIRONMENT', 'development')}")
        click.echo(f"Debug Mode: {'Enabled' if config.get('DEBUG') else 'Disabled'}")
        
        # Database
        db_uri = config.get('SQLALCHEMY_DATABASE_URI', '')
        masked_db_uri = db_uri
        if 'postgres' in db_uri and ':' in db_uri:
            # Mask password in database URI
            parts = db_uri.split(':', 3)
            if len(parts) >= 4:
                parts[2] = '****'
                masked_db_uri = ':'.join(parts)
        
        click.echo(f"Database: {masked_db_uri}")
        
        # API Simulation
        click.echo("\nAPI Simulation:")
        click.echo(f"  Meta API: {'Enabled' if config.get('META_API_SIMULATE') else 'Disabled'}")
        click.echo(f"  Google Ads API: {'Enabled' if config.get('GOOGLE_API_SIMULATE') else 'Disabled'}")
        click.echo(f"  Twitter API: {'Enabled' if config.get('TWITTER_API_SIMULATE') else 'Disabled'}")
        
        # API Framework
        click.echo("\nAPI Framework:")
        framework_enabled = config.get('USE_API_FRAMEWORK', False)
        click.echo(f"  Enabled: {'Yes' if framework_enabled else 'No'}")
        
        if framework_enabled:
            platforms = config.get('API_FRAMEWORK_PLATFORMS', [])
            if platforms:
                platforms_str = ", ".join(platforms)
                click.echo(f"  Platforms: {platforms_str}")
            else:
                click.echo("  Platforms: None")
            
            click.echo(f"  Collect Metrics: {'Yes' if config.get('COLLECT_API_METRICS', True) else 'No'}")
            click.echo(f"  Cache TTL: {config.get('API_CACHE_TTL', 300)} seconds")
        
        # API Rate Limits
        click.echo("\nAPI Rate Limits:")
        click.echo(f"  Meta API: {config.get('META_API_RATE_LIMIT', 'N/A')} requests/hour")
        click.echo(f"  Twitter API: {config.get('TWITTER_API_RATE_LIMIT', 'N/A')} requests/15min")
        click.echo(f"  Google API: {config.get('GOOGLE_API_RATE_LIMIT', 'N/A')} requests/100sec")
        
    @config.command('toggle-api-framework')
    @click.argument('enabled', type=bool)
    @click.option('--platforms', '-p', multiple=True, help='Platforms to enable')
    def toggle_api_framework_command(enabled, platforms):
        """Toggle API Framework on/off."""
        from app.utils.config import config_manager
        
        if enabled:
            # Enable the API Framework
            if platforms:
                config_manager.enable_api_framework(list(platforms))
                click.echo(f"API Framework enabled for platforms: {', '.join(platforms)}")
            else:
                config_manager.enable_api_framework()
                click.echo("API Framework enabled (no platforms specified)")
        else:
            # Disable the API Framework
            config_manager.disable_api_framework()
            click.echo("API Framework disabled")
        
        # Show current status
        config = config_manager.get_all()
        framework_enabled = config.get('USE_API_FRAMEWORK', False)
        platforms = config.get('API_FRAMEWORK_PLATFORMS', [])
        
        click.echo(f"\nCurrent status: {'Enabled' if framework_enabled else 'Disabled'}")
        if framework_enabled and platforms:
            click.echo(f"Active platforms: {', '.join(platforms)}")
            
    @config.command('cleanup-legacy')
    @click.option('--confirm', is_flag=True, help='Confirm the cleanup without prompting')
    def cleanup_legacy_command(confirm):
        """Remove legacy code after API Framework migration."""
        if not confirm:
            should_continue = click.confirm(
                "This will remove all legacy API code that has been replaced by the API Framework. Continue?",
                default=False
            )
            if not should_continue:
                click.echo("Operation cancelled.")
                return
        
        click.echo("Cleaning up legacy code...")
        
        # Import and run the cleanup script
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'cleanup_legacy_code.py')
        
        try:
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("Legacy code cleanup successful!")
                click.echo(result.stdout)
            else:
                click.echo(f"Error during cleanup: {result.stderr}")
                return 1
        except Exception as e:
            click.echo(f"Error running cleanup script: {str(e)}")
            return 1
    
    @app.cli.group()
    def users():
        """User management commands."""
        pass
    
    @users.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
    @click.option('--first-name', help='First name of the admin user')
    @click.option('--last-name', help='Last name of the admin user')
    def create_admin(username, email, password, first_name, last_name):
        """Create an admin user."""
        try:
            from app.models.user import User, UserRole
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                click.echo(f"User '{username}' already exists.")
                return
            
            # Create new admin user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.ADMIN.value,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            click.echo(f"Admin user '{username}' created successfully.")
        except Exception as e:
            click.echo(f"Error creating admin user: {str(e)}", err=True)
            return 1
    
    @users.command('list')
    def list_users():
        """List all users in the system."""
        try:
            from app.models.user import User
            
            users = User.query.all()
            if not users:
                click.echo("No users found in the system.")
                return
            
            click.echo("\nUsers in the system:")
            click.echo("ID | Username | Email | Role | Active | Last Login")
            click.echo("-" * 80)
            
            for user in users:
                last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
                click.echo(f"{user.id} | {user.username} | {user.email} | {user.role} | {'Yes' if user.is_active else 'No'} | {last_login}")
            
        except Exception as e:
            click.echo(f"Error listing users: {str(e)}", err=True)
            return 1