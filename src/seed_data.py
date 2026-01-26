"""
Comprehensive data seeder for Task Manager API.

This script creates a complete set of demonstration data including:
- Multiple users with different roles
- Tasks in various states (todo, in_progress, done)
- Tasks with different due date scenarios (overdue, upcoming, future)
- Comment threads on tasks
- Various types of notifications
- Task assignments across users

Usage:
    python -m src.seed_data
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.user import User, UserRole
from src.models.task import Task, TaskStatus
from src.models.comment import Comment
from src.models.notification import Notification, NotificationType
from src.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clear_existing_data(session):
    """Clear existing data to start fresh."""
    logger.info("🗑️  Clearing existing data...")
    
    # Delete in order of dependencies
    await session.execute(Notification.__table__.delete())
    await session.execute(Comment.__table__.delete())
    await session.execute(Task.__table__.delete())
    await session.execute(User.__table__.delete())
    
    await session.commit()
    logger.info("✅ Existing data cleared")


async def create_users(session):
    """Create demonstration users with different roles."""
    logger.info("👥 Creating users...")
    
    users_data = [
        {
            "email": "admin@admin.com",
            "password": "admin123",
            "role": UserRole.OWNER,
            "is_active": True
        },
        {
            "email": "john.doe@example.com",
            "password": "password123",
            "role": UserRole.MEMBER,
            "is_active": True
        },
        {
            "email": "jane.smith@example.com",
            "password": "password123",
            "role": UserRole.MEMBER,
            "is_active": True
        },
        {
            "email": "bob.wilson@example.com",
            "password": "password123",
            "role": UserRole.OWNER,
            "is_active": True
        },
        {
            "email": "alice.johnson@example.com",
            "password": "password123",
            "role": UserRole.MEMBER,
            "is_active": True
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        session.add(user)
        users.append(user)
        logger.info(f"  ✓ Created user: {user_data['email']} ({user_data['role'].value})")
    
    await session.commit()
    
    # Refresh to get IDs
    for user in users:
        await session.refresh(user)
    
    logger.info(f"✅ Created {len(users)} users")
    return users


async def create_tasks(session, users):
    """Create tasks with various states and due dates."""
    logger.info("📝 Creating tasks...")
    
    now = datetime.utcnow()
    
    tasks_data = [
        # OVERDUE TASKS (past due dates)
        {
            "title": "Critical Bug Fix - Payment Gateway",
            "description": "Payment gateway is failing for transactions over $1000. Multiple customers affected. Need immediate fix.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": now - timedelta(days=5),
            "owner": users[0]  # admin
        },
        {
            "title": "Update Production Database Schema",
            "description": "Migration scripts need to be run on production. Scheduled for last week but pending approval.",
            "status": TaskStatus.TODO,
            "due_date": now - timedelta(days=3),
            "owner": users[1]  # john.doe
        },
        {
            "title": "Security Audit Report",
            "description": "Complete security audit and submit report to compliance team.",
            "status": TaskStatus.TODO,
            "due_date": now - timedelta(days=2),
            "owner": users[2]  # jane.smith
        },
        {
            "title": "Q4 Performance Review Meetings",
            "description": "Conduct one-on-one performance reviews with all team members.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": now - timedelta(days=1),
            "owner": users[3]  # bob.wilson
        },
        
        # UPCOMING TASKS (due soon - next 3 days)
        {
            "title": "Deploy v2.5.0 to Production",
            "description": "Deploy the new release with performance improvements and bug fixes. Coordinate with DevOps team.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": now + timedelta(hours=12),
            "owner": users[0]  # admin
        },
        {
            "title": "Client Demo Preparation",
            "description": "Prepare demo environment and presentation materials for potential enterprise client.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=1),
            "owner": users[4]  # alice.johnson
        },
        {
            "title": "Code Review - Authentication Module",
            "description": "Review pull request #234 for the new OAuth2 implementation. Check for security vulnerabilities.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=2),
            "owner": users[1]  # john.doe
        },
        {
            "title": "API Documentation Update",
            "description": "Update OpenAPI documentation to reflect recent endpoint changes and new features.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": now + timedelta(days=3),
            "owner": users[2]  # jane.smith
        },
        
        # FUTURE TASKS (due later - more than 3 days out)
        {
            "title": "Implement Dark Mode for Dashboard",
            "description": "Add dark mode theme option to the admin dashboard. Should persist user preference.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=7),
            "owner": users[1]  # john.doe
        },
        {
            "title": "Database Performance Optimization",
            "description": "Analyze slow queries and add necessary indexes. Target 50% improvement in response times.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=10),
            "owner": users[0]  # admin
        },
        {
            "title": "Mobile App Responsive Design",
            "description": "Optimize UI for mobile devices. Focus on tablet and smartphone layouts.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=14),
            "owner": users[2]  # jane.smith
        },
        {
            "title": "Integration with Slack Notifications",
            "description": "Implement Slack webhook integration for task updates and team notifications.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=21),
            "owner": users[4]  # alice.johnson
        },
        {
            "title": "Q1 2026 Planning Meeting",
            "description": "Organize and conduct quarterly planning session. Set OKRs for the next quarter.",
            "status": TaskStatus.TODO,
            "due_date": now + timedelta(days=30),
            "owner": users[3]  # bob.wilson
        },
        
        # COMPLETED TASKS (various completion dates)
        {
            "title": "Setup CI/CD Pipeline",
            "description": "Configured GitHub Actions for automated testing and deployment to staging environment.",
            "status": TaskStatus.DONE,
            "due_date": now - timedelta(days=10),
            "owner": users[0]  # admin
        },
        {
            "title": "User Onboarding Tutorial",
            "description": "Created interactive tutorial for new users covering basic features.",
            "status": TaskStatus.DONE,
            "due_date": now - timedelta(days=7),
            "owner": users[4]  # alice.johnson
        },
        {
            "title": "Fix Login Page Layout Bug",
            "description": "Resolved CSS issue causing misalignment on Firefox browser.",
            "status": TaskStatus.DONE,
            "due_date": now + timedelta(days=1),  # Completed early
            "owner": users[1]  # john.doe
        },
        {
            "title": "Weekly Team Standup",
            "description": "Regular Monday morning sync-up meeting with development team.",
            "status": TaskStatus.DONE,
            "due_date": now - timedelta(days=4),
            "owner": users[3]  # bob.wilson
        },
        
        # TASKS WITHOUT DUE DATES
        {
            "title": "Refactor Legacy Code in Auth Module",
            "description": "Technical debt: Clean up old authentication code and improve test coverage.",
            "status": TaskStatus.TODO,
            "due_date": None,
            "owner": users[1]  # john.doe
        },
        {
            "title": "Research AI Integration Possibilities",
            "description": "Explore potential use cases for AI/ML features in the platform. Create feasibility report.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": None,
            "owner": users[2]  # jane.smith
        },
        {
            "title": "Improve Error Handling",
            "description": "Add better error messages and logging throughout the application.",
            "status": TaskStatus.TODO,
            "due_date": None,
            "owner": users[0]  # admin
        },
        {
            "title": "Knowledge Base Documentation",
            "description": "Create comprehensive documentation for internal processes and best practices.",
            "status": TaskStatus.IN_PROGRESS,
            "due_date": None,
            "owner": users[4]  # alice.johnson
        }
    ]
    
    tasks = []
    for task_data in tasks_data:
        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            status=task_data["status"],
            due_date=task_data["due_date"],
            owner_id=task_data["owner"].id
        )
        session.add(task)
        tasks.append(task)
        
        due_date_str = task_data["due_date"].strftime("%Y-%m-%d") if task_data["due_date"] else "No due date"
        logger.info(f"  ✓ Created task: {task_data['title'][:50]}... ({task_data['status'].value}, {due_date_str})")
    
    await session.commit()
    
    # Refresh to get IDs
    for task in tasks:
        await session.refresh(task)
    
    logger.info(f"✅ Created {len(tasks)} tasks")
    return tasks


async def create_comments(session, tasks, users):
    """Create comment threads on various tasks."""
    logger.info("💬 Creating comments...")
    
    comments_data = [
        # Thread on "Critical Bug Fix - Payment Gateway" (task 0)
        {
            "task": tasks[0],
            "user": users[0],  # admin
            "content": "I'm looking into this now. Initial investigation shows it might be related to the recent Stripe API update."
        },
        {
            "task": tasks[0],
            "user": users[1],  # john.doe
            "content": "I noticed the same issue yesterday. The logs show a 400 error from the payment provider. Here's the stack trace: [link to logs]"
        },
        {
            "task": tasks[0],
            "user": users[3],  # bob.wilson
            "content": "This is affecting our biggest client. Can we get an ETA on the fix? Should we roll back the deployment?"
        },
        {
            "task": tasks[0],
            "user": users[0],  # admin
            "content": "Fix is ready for testing. We're not rolling back - I've implemented a workaround that handles the new API response format. QA testing now."
        },
        {
            "task": tasks[0],
            "user": users[2],  # jane.smith
            "content": "QA passed! Ready to deploy. The workaround is solid and handles edge cases well."
        },
        
        # Thread on "Deploy v2.5.0 to Production" (task 4)
        {
            "task": tasks[4],
            "user": users[0],  # admin
            "content": "Deployment checklist:\n1. Database migrations ✅\n2. Feature flags configured ✅\n3. Monitoring alerts set up ✅\n4. Rollback plan ready ✅"
        },
        {
            "task": tasks[4],
            "user": users[1],  # john.doe
            "content": "Don't forget to warm up the cache after deployment to avoid cold start issues."
        },
        {
            "task": tasks[4],
            "user": users[0],  # admin
            "content": "Good catch! Added to the checklist. Will run the cache warming script immediately after deployment."
        },
        
        # Thread on "Client Demo Preparation" (task 5)
        {
            "task": tasks[5],
            "user": users[4],  # alice.johnson
            "content": "Demo environment is set up. Using the staging server with demo data populated."
        },
        {
            "task": tasks[5],
            "user": users[3],  # bob.wilson
            "content": "Great! Make sure to highlight the new real-time collaboration features and the improved dashboard analytics."
        },
        {
            "task": tasks[5],
            "user": users[4],  # alice.johnson
            "content": "Will do! I've prepared a 30-minute walkthrough focusing on those features plus the API integration capabilities."
        },
        
        # Thread on "Database Performance Optimization" (task 9)
        {
            "task": tasks[9],
            "user": users[0],  # admin
            "content": "Starting with the slow query analysis. I've identified 5 queries that are taking >2 seconds on average."
        },
        {
            "task": tasks[9],
            "user": users[1],  # john.doe
            "content": "The user tasks query is definitely one of them. It's doing a full table scan. We need a composite index on (user_id, status)."
        },
        {
            "task": tasks[9],
            "user": users[0],  # admin
            "content": "Agreed. I'll create an index optimization PR. Also found that we're missing indexes on foreign keys in the notifications table."
        },
        
        # Thread on "Setup CI/CD Pipeline" (task 13 - completed)
        {
            "task": tasks[13],
            "user": users[0],  # admin
            "content": "Pipeline is live! We now have:\n- Automated tests on every PR\n- Auto-deploy to staging on main branch\n- Manual approval for production deploys"
        },
        {
            "task": tasks[13],
            "user": users[2],  # jane.smith
            "content": "This is awesome! Deploy time went from 45 minutes to 8 minutes. Huge improvement! 🚀"
        },
        {
            "task": tasks[13],
            "user": users[3],  # bob.wilson
            "content": "Excellent work! This will significantly speed up our release cycle."
        },
        
        # Thread on "Research AI Integration Possibilities" (task 18)
        {
            "task": tasks[18],
            "user": users[2],  # jane.smith
            "content": "Initial research complete. Top 3 opportunities:\n1. Smart task prioritization\n2. Automated task categorization\n3. Predictive deadline estimation"
        },
        {
            "task": tasks[18],
            "user": users[0],  # admin
            "content": "Smart task prioritization sounds promising. How would that work?"
        },
        {
            "task": tasks[18],
            "user": users[2],  # jane.smith
            "content": "ML model trained on completed tasks could predict priority based on title, description, and historical patterns. Could boost team productivity by 20-30%."
        },
        {
            "task": tasks[18],
            "user": users[3],  # bob.wilson
            "content": "Let's schedule a meeting to discuss implementation timeline and resource requirements."
        },
        
        # Single comments on other tasks
        {
            "task": tasks[2],
            "user": users[3],  # bob.wilson
            "content": "This is urgent. Compliance deadline cannot be missed. Let me know if you need any resources."
        },
        {
            "task": tasks[6],
            "user": users[0],  # admin
            "content": "Pay special attention to the token validation logic. Security is critical here."
        },
        {
            "task": tasks[7],
            "user": users[1],  # john.doe
            "content": "I can help with this if you need a second pair of eyes on the documentation structure."
        },
        {
            "task": tasks[10],
            "user": users[0],  # admin
            "content": "Make sure to test on both iOS Safari and Chrome. The CSS Grid behavior differs between them."
        },
        {
            "task": tasks[11],
            "user": users[3],  # bob.wilson
            "content": "This would be a great addition. Many teams are requesting better notification integrations."
        },
        {
            "task": tasks[19],
            "user": users[0],  # admin
            "content": "Focus on the authentication and authorization modules first - they have the highest complexity."
        }
    ]
    
    comments = []
    for comment_data in comments_data:
        comment = Comment(
            content=comment_data["content"],
            task_id=comment_data["task"].id,
            author_id=comment_data["user"].id
        )
        session.add(comment)
        comments.append(comment)
    
    await session.commit()
    
    logger.info(f"✅ Created {len(comments)} comments across {len(set(c['task'] for c in comments_data))} tasks")
    return comments


async def create_notifications(session, tasks, users):
    """Create various types of notifications."""
    logger.info("🔔 Creating notifications...")
    
    now = datetime.utcnow()
    
    notifications_data = [
        # OVERDUE notifications
        {
            "user": users[0],  # admin
            "task": tasks[0],  # Critical Bug Fix
            "notification_type": NotificationType.OVERDUE,
            "message": "Task 'Critical Bug Fix - Payment Gateway' is overdue by 5 days",
            "is_read": False,
            "created_at": now - timedelta(hours=2)
        },
        {
            "user": users[1],  # john.doe
            "task": tasks[1],  # Update Production Database
            "notification_type": NotificationType.OVERDUE,
            "message": "Task 'Update Production Database Schema' is overdue by 3 days",
            "is_read": False,
            "created_at": now - timedelta(hours=5)
        },
        {
            "user": users[2],  # jane.smith
            "task": tasks[2],  # Security Audit
            "notification_type": NotificationType.OVERDUE,
            "message": "Task 'Security Audit Report' is overdue by 2 days",
            "is_read": True,
            "created_at": now - timedelta(days=1)
        },
        {
            "user": users[3],  # bob.wilson
            "task": tasks[3],  # Q4 Performance Review
            "notification_type": NotificationType.OVERDUE,
            "message": "Task 'Q4 Performance Review Meetings' was due yesterday",
            "is_read": False,
            "created_at": now - timedelta(hours=8)
        },
        
        # DUE_SOON notifications
        {
            "user": users[0],  # admin
            "task": tasks[4],  # Deploy v2.5.0
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Deploy v2.5.0 to Production' is due in 12 hours",
            "is_read": False,
            "created_at": now - timedelta(minutes=30)
        },
        {
            "user": users[4],  # alice.johnson
            "task": tasks[5],  # Client Demo
            "notification_type": NotificationType.DUE_TODAY,
            "message": "Task 'Client Demo Preparation' is due today",
            "is_read": False,
            "created_at": now - timedelta(hours=1)
        },
        {
            "user": users[1],  # john.doe
            "task": tasks[6],  # Code Review
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Code Review - Authentication Module' is due in 2 days",
            "is_read": True,
            "created_at": now - timedelta(days=2)
        },
        {
            "user": users[2],  # jane.smith
            "task": tasks[7],  # API Documentation
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'API Documentation Update' is due in 3 days",
            "is_read": False,
            "created_at": now - timedelta(hours=4)
        },
        {
            "user": users[1],  # john.doe
            "task": tasks[8],  # Dark Mode
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Implement Dark Mode for Dashboard' is due in 7 days",
            "is_read": True,
            "created_at": now - timedelta(days=3)
        },
        {
            "user": users[4],  # alice.johnson
            "task": tasks[11],  # Slack Integration
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Integration with Slack Notifications' is due in 21 days",
            "is_read": False,
            "created_at": now - timedelta(days=1)
        },
        {
            "user": users[2],  # jane.smith
            "task": tasks[10],  # Mobile Responsive
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Mobile App Responsive Design' is due in 14 days",
            "is_read": False,
            "created_at": now - timedelta(hours=12)
        },
        {
            "user": users[0],  # admin
            "task": tasks[9],  # Database Performance
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Database Performance Optimization' is due in 10 days",
            "is_read": True,
            "created_at": now - timedelta(days=4)
        },
        {
            "user": users[3],  # bob.wilson
            "task": tasks[12],  # Q1 Planning
            "notification_type": NotificationType.DUE_SOON,
            "message": "Task 'Q1 2026 Planning Meeting' is due in 30 days",
            "is_read": False,
            "created_at": now - timedelta(hours=6)
        },
        
        # DUE_TODAY notifications
        {
            "user": users[0],  # admin
            "task": tasks[4],  # Deploy v2.5.0
            "notification_type": NotificationType.DUE_TODAY,
            "message": "Task 'Deploy v2.5.0 to Production' is due today!",
            "is_read": False,
            "created_at": now - timedelta(minutes=15)
        },
        {
            "user": users[4],  # alice.johnson
            "task": tasks[5],  # Client Demo
            "notification_type": NotificationType.DUE_TODAY,
            "message": "Task 'Client Demo Preparation' is due today!",
            "is_read": False,
            "created_at": now - timedelta(minutes=45)
        }
    ]
    
    notifications = []
    for notif_data in notifications_data:
        notification = Notification(
            user_id=notif_data["user"].id,
            task_id=notif_data["task"].id,
            notification_type=notif_data["notification_type"],
            message=notif_data["message"],
            is_read=notif_data["is_read"],
            created_at=notif_data["created_at"]
        )
        session.add(notification)
        notifications.append(notification)
    
    await session.commit()
    
    unread_count = sum(1 for n in notifications_data if not n["is_read"])
    logger.info(f"✅ Created {len(notifications)} notifications ({unread_count} unread)")
    return notifications


async def seed_database():
    """Main seeder function that orchestrates all data creation."""
    logger.info("🌱 Starting database seeding process...\n")
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Create data in order
            users = await create_users(session)
            tasks = await create_tasks(session, users)
            comments = await create_comments(session, tasks, users)
            notifications = await create_notifications(session, tasks, users)
            
            logger.info("\n" + "="*80)
            logger.info("🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY!")
            logger.info("="*80)
            logger.info(f"""
📊 Summary:
   • Users: {len(users)}
   • Tasks: {len(tasks)}
   • Comments: {len(comments)}
   • Notifications: {len(notifications)} ({sum(1 for n in notifications if not n.is_read)} unread)

🔐 Login Credentials:
   • admin@admin.com / admin123 (OWNER)
   • john.doe@example.com / password123 (MEMBER)
   • jane.smith@example.com / password123 (MEMBER)
   • bob.wilson@example.com / password123 (OWNER)
   • alice.johnson@example.com / password123 (MEMBER)

🚀 Next Steps:
   1. Start the API: uvicorn src.main:app --reload
   2. Start the frontend: cd frontend && npm run dev
   3. Login with any of the credentials above
   4. Explore all the features!
            """)
            logger.info("="*80 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Error during seeding: {str(e)}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
