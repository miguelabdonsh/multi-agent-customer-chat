-- Multi-Agent Customer Chat Database Schema
-- Minimal, efficient schema for production use

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Chat sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'escalated')),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    sender VARCHAR(100) NOT NULL CHECK (sender IN ('user', 'router', 'faq', 'support', 'guardrails', 'escalation', 'assistant')),
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'system', 'error')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Knowledge base for FAQ agent
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Escalation tracking
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'resolved')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_to VARCHAR(255),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_base_keywords ON knowledge_base USING GIN(keywords);
CREATE INDEX idx_escalations_session_id ON escalations(session_id);
CREATE INDEX idx_escalations_status ON escalations(status);

-- Comprehensive FAQ data for software company support
INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
-- Account Management
('account', 'How do I create a new account?', 'Visit our website and click "Sign Up" in the top right corner. You will need to provide your email address and create a password.', ARRAY['signup', 'register', 'new account', 'create account']),
('account', 'How do I reset my password?', 'Click "Forgot Password" on the login page and enter your email address. You will receive a password reset link within 5 minutes.', ARRAY['password', 'reset', 'forgot', 'login', 'recovery']),
('account', 'How do I change my email address?', 'Go to Account Settings > Profile and click "Edit" next to your email. You will need to verify the new email address.', ARRAY['email', 'change', 'update', 'profile', 'settings']),
('account', 'How do I delete my account?', 'Contact our support team through this chat or email support@company.com. We will guide you through the account deletion process.', ARRAY['delete', 'close', 'remove', 'account', 'terminate']),

-- Billing and Payments
('billing', 'What payment methods do you accept?', 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for annual plans.', ARRAY['payment', 'credit card', 'paypal', 'billing', 'methods']),
('billing', 'How do I update my billing information?', 'Go to Account Settings > Billing and click "Update Payment Method". You can add or modify your payment information there.', ARRAY['billing', 'payment', 'update', 'credit card', 'method']),
('billing', 'When am I charged for my subscription?', 'You are charged on the same date each month or year, depending on your billing cycle. You can view your next billing date in Account Settings > Billing.', ARRAY['billing', 'charge', 'subscription', 'date', 'payment']),
('billing', 'How do I cancel my subscription?', 'Go to Account Settings > Billing and click "Cancel Subscription". Your access will continue until the end of your current billing period.', ARRAY['cancel', 'subscription', 'billing', 'terminate', 'stop']),
('billing', 'Do you offer refunds?', 'We offer a 30-day money-back guarantee for new subscriptions. Contact support within 30 days of your first payment for a full refund.', ARRAY['refund', 'money back', 'guarantee', '30 days', 'return']),

-- Product Features
('features', 'How do I invite team members?', 'Go to Team Settings and click "Invite Member". Enter their email address and select their role. They will receive an invitation email.', ARRAY['invite', 'team', 'member', 'collaboration', 'user']),
('features', 'How do I export my data?', 'Go to Settings > Data Export and select the data you want to export. You can download it as CSV, JSON, or PDF format.', ARRAY['export', 'data', 'download', 'backup', 'csv']),
('features', 'How do I set up integrations?', 'Go to Settings > Integrations and click "Add Integration". We support popular tools like Slack, Zapier, and Google Workspace.', ARRAY['integration', 'connect', 'slack', 'zapier', 'google']),
('features', 'How do I customize my dashboard?', 'Click the gear icon in the top right of your dashboard to access customization options. You can add, remove, or rearrange widgets.', ARRAY['dashboard', 'customize', 'widget', 'layout', 'personalize']),

-- Technical Issues
('technical', 'The app is loading slowly, what should I do?', 'Try refreshing your browser, clearing your cache, or using a different browser. If the issue persists, contact our support team.', ARRAY['slow', 'loading', 'performance', 'browser', 'cache']),
('technical', 'I cannot log in to my account', 'First, check that your email and password are correct. If you forgot your password, use the "Forgot Password" link. If issues persist, contact support.', ARRAY['login', 'access', 'password', 'authentication', 'signin']),
('technical', 'The app is not working on my mobile device', 'Our mobile app is available for iOS and Android. Download it from the App Store or Google Play Store. For mobile web, try using Chrome or Safari.', ARRAY['mobile', 'app', 'ios', 'android', 'phone', 'tablet']),
('technical', 'I am getting an error message', 'Please note the exact error message and contact our support team. Include your browser type and version for faster resolution.', ARRAY['error', 'bug', 'issue', 'problem', 'message']),

-- Security
('security', 'Is my data secure?', 'Yes, we use industry-standard encryption and security practices. All data is encrypted in transit and at rest. We are SOC 2 compliant and regularly audit our security.', ARRAY['security', 'encryption', 'safe', 'protect', 'privacy']),
('security', 'How do I enable two-factor authentication?', 'Go to Account Settings > Security and click "Enable 2FA". You can use an authenticator app or receive SMS codes.', ARRAY['2fa', 'two factor', 'security', 'authentication', 'mfa']),
('security', 'I received a suspicious email from your company', 'We will never ask for your password via email. If you received a suspicious email, forward it to security@company.com and do not click any links.', ARRAY['phishing', 'email', 'suspicious', 'security', 'scam']),

-- API and Development
('api', 'How do I get an API key?', 'Go to Settings > API Keys and click "Generate New Key". Keep your API key secure and never share it publicly.', ARRAY['api', 'key', 'token', 'developer', 'integration']),
('api', 'What are the API rate limits?', 'Free accounts have 1000 requests per hour. Paid plans have higher limits. Check your current usage in Settings > API Keys.', ARRAY['api', 'rate limit', 'requests', 'quota', 'usage']),
('api', 'How do I integrate your API into my application?', 'Check our API documentation at docs.company.com for detailed guides and code examples in multiple programming languages.', ARRAY['api', 'integration', 'documentation', 'code', 'develop']),

-- General Support
('general', 'What are your business hours?', 'Our support team is available Monday to Friday, 9 AM to 6 PM EST. For urgent issues outside these hours, email support@company.com.', ARRAY['hours', 'support', 'time', 'business', 'available']),
('general', 'How can I contact support?', 'You can reach us through this chat, email at support@company.com, or call 1-800-SUPPORT during business hours.', ARRAY['contact', 'support', 'help', 'phone', 'email']),
('general', 'Do you offer training or onboarding?', 'Yes, we offer free onboarding sessions for new customers. Contact your account manager or email onboarding@company.com to schedule.', ARRAY['training', 'onboarding', 'setup', 'help', 'learn']),
('general', 'Where can I find documentation?', 'Visit our help center at help.company.com for guides, tutorials, and frequently asked questions. We also have video tutorials available.', ARRAY['documentation', 'help', 'guide', 'tutorial', 'learn']);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 