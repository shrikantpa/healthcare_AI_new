# Testing & Deployment Guide

## Frontend & Backend Integration

### Starting the System

#### Step 1: Start Backend API Server
```bash
cd /workspaces/healthcare_data_analytics/backend
source ../venv/bin/activate
python main.py
```
Backend will run at: `http://localhost:8000`

#### Step 2: Serve Frontend Files
```bash
cd /workspaces/healthcare_data_analytics/frontend
python -m http.server 8001
```
Frontend will run at: `http://localhost:8001`

#### Step 3: Access the Application
Open your browser and navigate to:
```
http://localhost:8001/index.html
```

### Testing Scenarios

#### Scenario 1: Login with Default User
1. Navigate to login page
2. Username: `admin`
3. Password: `admin123`
4. Click "Login"
5. Expected: Redirect to dashboard.html with user info

#### Scenario 2: Signup with Valid Location
1. Click "Register here" link
2. First Name: `John`
3. Last Name: `Doe`
4. State: Select `West Bengal`
5. District: Select `Bankura` (should be filtered)
6. Username: `johndoe_test`
7. Password: `Test@123`
8. Confirm Password: `Test@123`
9. Click "Sign Up"
10. Expected: Success modal → Link to login page

#### Scenario 3: Signup with Invalid Location
1. Click "Register here"
2. Fill form with valid data
3. State: Select `West Bengal`
4. District: Manually type "InvalidDistrict" (if allowed) or select invalid combo
5. Click "Sign Up"
6. Expected: Error message "Location not found"

#### Scenario 4: Signup with Duplicate Username
1. First signup user successfully (Scenario 2)
2. Try signup with same username again
3. Expected: Error "Username already exists"

#### Scenario 5: Password Mismatch
1. In signup page
2. Password: `Test@123`
3. Confirm Password: `Test@456`
4. Expected: Red error indicator and form cannot submit

#### Scenario 6: Logout
1. After successful login/signup
2. Click "Logout" button
3. Expected: Return to login page, localStorage cleared

### Available Test Districts

Available combinations in the system:
- Uttar Pradesh: Etah
- West Bengal: Bankura
- Puducherry: Karaikal
- The Dadra And Nagar Haveli And Daman And Diu: Dadra And Nagar

### API Testing

#### Test Login Endpoint
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### Test Signup Endpoint
```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name":"Jane",
    "last_name":"Smith",
    "username":"janesmith_test",
    "password":"Test@123",
    "district":"Bankura",
    "state":"West Bengal"
  }'
```

#### Test Locations Endpoint
```bash
curl http://localhost:8000/locations
```

### Browser Developer Tools Checks

#### Check Console
1. Open DevTools (F12)
2. Go to Console tab
3. Look for any JavaScript errors
4. Verify API calls in Network tab

#### Check Network
1. Open DevTools (F12)
2. Go to Network tab
3. Submit login/signup form
4. Verify API calls:
   - POST /login or /signup
   - GET /locations
5. Check response status (200, 400, 500, etc.)

#### Check Storage
1. Open DevTools (F12)
2. Go to Application tab
3. Check localStorage:
   - `user` - should contain user JSON
   - `token` - should contain username

### Troubleshooting

#### Frontend Not Loading
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill process if needed
kill -9 <PID>
```

#### API Connection Failed
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check API status
curl http://localhost:8000/
```

#### CORS Error
- Ensure backend has CORS middleware enabled
- Check backend logs for errors
- Verify API_BASE_URL in auth.js matches backend URL

#### Dropdown Not Loading
1. Check Network tab → /locations endpoint
2. Verify response contains data
3. Check browser console for JavaScript errors
4. Ensure backend database is initialized

#### Login Not Working
1. Verify username/password are correct
2. Check backend database for user_mapping table
3. Verify user credentials match exactly
4. Check backend logs for errors

### Performance Testing

#### Load Testing API
```bash
# Simple load test on login endpoint
for i in {1..10}; do
  curl -X POST http://localhost:8000/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' &
done
```

#### Check Response Times
1. Open Network tab
2. Monitor request times
3. Should complete in <500ms typically
4. Check for any slow endpoints

### Database Verification

#### Check Users Table
```bash
sqlite3 backend/malaria_data.db
SELECT * FROM users;
.schema users
```

#### Check Location Table
```bash
sqlite3 backend/malaria_data.db
SELECT DISTINCT state, district FROM location;
```

#### Verify User Creation
```bash
sqlite3 backend/malaria_data.db
SELECT first_name, last_name, username, district, state FROM users WHERE username='johndoe_test';
```

### Production Deployment Notes

1. **Update API_BASE_URL** in auth.js to production backend URL
2. **Enable HTTPS** on both frontend and backend
3. **Update CORS settings** to specific domain
4. **Use environment variables** for sensitive data
5. **Implement proper authentication tokens** (JWT recommended)
6. **Add rate limiting** on signup/login endpoints
7. **Store passwords securely** (use bcrypt)
8. **Add email verification** for signup
9. **Implement session timeout**
10. **Add CSRF protection**

### Frontend Deployment Options

#### Option 1: Static Hosting
- Upload to AWS S3
- Use CloudFront for CDN
- Update API_BASE_URL to production backend

#### Option 2: Simple HTTP Server
```bash
python -m http.server 8001 --directory /path/to/frontend
```

#### Option 3: Docker Container
```dockerfile
FROM python:3.9
WORKDIR /app
COPY frontend/ .
CMD ["python", "-m", "http.server", "8001"]
```

#### Option 4: Node HTTP Server
```bash
npm install -g http-server
http-server frontend/ -p 8001
```

### Monitoring & Logging

#### Frontend Console Monitoring
```javascript
// Add this to auth.js to log all API calls
window.addEventListener('fetch', (event) => {
    console.log('API Call:', event.request.method, event.request.url);
});
```

#### Backend Logging
Check backend logs for:
- Failed login attempts
- Signup validation failures
- API errors
- Database issues

### Cleanup & Reset

#### Clear Frontend Cache
```bash
# Clear localStorage
localStorage.clear();

# Clear browser cache
# Use browser DevTools or clear browser data
```

#### Reset Database
```bash
# Remove database file
rm backend/malaria_data.db

# Restart backend - database will be recreated
python backend/main.py
```

### System Health Checks

Use this checklist before going live:

- [ ] Backend API is running and accessible
- [ ] Frontend is being served properly
- [ ] Login endpoint works with default credentials
- [ ] Signup endpoint validates locations correctly
- [ ] Locations API returns expected data
- [ ] Dropdowns populate correctly
- [ ] Password validation works
- [ ] Error messages display properly
- [ ] Success messages and modals show
- [ ] Logout functionality works
- [ ] localStorage properly saves user data
- [ ] Mobile responsiveness tested
- [ ] All API calls visible in Network tab
- [ ] No console errors
- [ ] Network requests complete successfully (200 status)

## Summary

The Aayura authentication system is now fully functional with:
✅ Responsive login page
✅ Multi-field signup form
✅ Location validation with cascading dropdowns
✅ Password matching validation
✅ Error handling and user feedback
✅ Success modals and redirects
✅ Session management via localStorage
✅ Full API integration with backend

Ready for testing and deployment!
