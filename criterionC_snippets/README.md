# CriterionC Code Snippets for IB DP Computer Science IA

This directory contains extracted code snippets from the Learning Management System project for use in the IB DP Computer Science Internal Assessment documentation, specifically for Criterion C (Development).

## Files Overview

### snippet1_auth_flow.py
- **Purpose**: Demonstrates user authentication and role-based access control
- **Source**: `routes/auth.py`, lines 17-47
- **Key Features**: 
  - Password hashing and verification
  - Session management
  - Role-based redirection (admin/teacher/student)

### snippet2_teacher_access_control.py  
- **Purpose**: Shows access control for teacher permissions and class assignments
- **Source**: `routes/teacher.py`, lines 61-81 and access verification functions
- **Key Features**:
  - Teacher-class assignment verification
  - Subject permission checking
  - SQL joins for data retrieval

### snippet3_weighted_grade_calculation.py
- **Purpose**: Demonstrates algorithmic calculation of weighted grades
- **Source**: `routes/teacher.py`, lines 870-890
- **Key Features**:
  - Weighted average calculation algorithm
  - Assessment score aggregation
  - Mathematical percentage conversion

### snippet4_database_triggers.sql
- **Purpose**: Shows database-level business logic automation
- **Source**: `database/schema.sql`, lines 385-420
- **Key Features**:
  - Automatic timestamp updates
  - Business rule enforcement
  - Data integrity triggers

### snippet5_batch_marks_processing.py
- **Purpose**: Demonstrates batch data processing with transaction handling
- **Source**: `routes/teacher.py`, lines 665-750
- **Key Features**:
  - Batch processing algorithm
  - Transaction management
  - Error handling and validation

### snippet6_attendance_aggregation.py
- **Purpose**: Shows data aggregation and statistical analysis
- **Source**: `routes/teacher.py` and `routes/admin.py` attendance functions
- **Key Features**:
  - SQL aggregation functions (GROUP BY, COUNT)
  - Statistical calculations
  - Data trend analysis

## Usage for IA Documentation

These snippets are designed to be:
1. **Self-contained**: Each file focuses on a specific algorithmic or technical concept
2. **Well-commented**: Clear explanations of purpose and functionality
3. **Screenshot-ready**: Formatted for easy capture in documentation
4. **Evidence-based**: Directly extracted from working code with line references

## Code Attribution

All code snippets are extracted from the original LMS project files with proper source attribution. The original project structure and full implementation can be found in the parent directory.

## Note on Lint Errors

The lint errors shown in these files are expected, as these are extracted snippets that reference functions and imports from the main application context. In the full application, all dependencies are properly imported and defined.
