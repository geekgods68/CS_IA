-- Seed roles and admin user


-- Insert roles into user_roles
INSERT INTO user_roles (role_name, description) VALUES
    ('admin', 'Administrator'),
    ('teacher', 'Teaching Volunteer'),
    ('student', 'Student User');

-- Insert one admin user

-- Password for admin user is 'admin123'
-- Hash: scrypt:32768:8:1$mB25r8Cmq2vMmhe3$bac1dc2979c6d06201517796ac050e2151f94b9ebfa670b20de3beafa0008329cb15ed08a7e53a6753a4e3b99673985c15b96578b979eaa5f2025870ba1fa6d8


INSERT INTO users (
    username, password,
    created_by, created_on, updated_by, updated_on
) VALUES (
    'admin',
    'scrypt:32768:8:1$mB25r8Cmq2vMmhe3$bac1dc2979c6d06201517796ac050e2151f94b9ebfa670b20de3beafa0008329cb15ed08a7e53a6753a4e3b99673985c15b96578b979eaa5f2025870ba1fa6d8',
    NULL,
    CURRENT_TIMESTAMP,
    NULL,
    CURRENT_TIMESTAMP
);

-- Map admin user to admin role
INSERT INTO user_role_map (user_id, role_id, assigned_on, assigned_by)
VALUES (
    (SELECT id FROM users WHERE username = 'admin'),
    (SELECT id FROM user_roles WHERE role_name = 'admin'),
    CURRENT_TIMESTAMP,
    NULL
);
-- Seed sample class
INSERT INTO classes (name, grade, batch) VALUES ('Class 10', '10', 'A');

-- Seed sample subjects
INSERT INTO subjects (class_id, name, description) VALUES (1, 'Mathematics', 'Math for Class 10');
INSERT INTO subjects (class_id, name, description) VALUES (1, 'Science', 'Science for Class 10');