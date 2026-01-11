# FaithConnect API Quick Reference

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All endpoints (except register/login) require JWT token:
```
Authorization: Bearer <your-jwt-token>
```

---

## 📌 Quick Links
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

---

## 🔐 Authentication

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe",
  "role": "worshiper",  // or "leader"
  "faith": "Christianity"  // required for worshipers
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response: { "access_token": "eyJ0...", "token_type": "bearer" }
```

### Get Profile
```http
GET /auth/me
Authorization: Bearer <token>
```

---

## 👥 Follows

### Follow Leader
```http
POST /follows/{leader_id}
Authorization: Bearer <worshiper-token>
```

### Unfollow Leader
```http
DELETE /follows/{leader_id}
Authorization: Bearer <worshiper-token>
```

### Get Following List
```http
GET /follows/following
Authorization: Bearer <worshiper-token>
```

### Get Followers (Leaders Only)
```http
GET /follows/followers
Authorization: Bearer <leader-token>
```

---

## 📰 Feed

### Explore Feed (All Posts)
```http
GET /feed/explore?limit=20&offset=0
Authorization: Bearer <token>
```

### Following Feed (Posts from Followed Leaders)
```http
GET /feed/following?limit=20&offset=0
Authorization: Bearer <worshiper-token>
```

### Daily Reflection (Featured Post)
```http
GET /feed/daily-reflection
Authorization: Bearer <token>
```

---

## 📝 Posts

### Create Post (Leaders Only)
```http
POST /posts
Authorization: Bearer <leader-token>
Content-Type: application/json

{
  "content_text": "Today's reflection on faith and hope...",
  "media_url": "https://example.com/image.jpg",
  "media_type": "IMAGE",
  "tag": "REFLECTION",
  "intent": "INSPIRE",
  "scheduled_at": "2026-01-10T10:00:00Z"  // optional
}
```

**Tags**: TEACHING, REFLECTION, PRAYER, TESTIMONY, QUESTION  
**Intents**: INSPIRE, GUIDE, COMFORT, CHALLENGE, EDUCATE  
**Media Types**: IMAGE, VIDEO, AUDIO

### Get Leader's Posts
```http
GET /posts
Authorization: Bearer <leader-token>
```

---

## ❓ Questions

### Ask Question (Worshipers Only)
```http
POST /questions/{leader_id}
Authorization: Bearer <worshiper-token>
Content-Type: application/json

{
  "question_text": "How can I strengthen my faith during difficult times?"
}
```

### View Question Inbox (Leaders Only)
```http
GET /questions
Authorization: Bearer <leader-token>

Response: {
  "pending": [...],   // unanswered questions
  "answered": [...]   // answered questions
}
```

### Answer Question (Leaders Only)
```http
POST /questions/{question_id}/answer
Authorization: Bearer <leader-token>
Content-Type: application/json

{
  "answer_text": "Dear friend, strengthening faith requires..."
}
```

---

## 💙 Engagement

### Like Post
```http
POST /posts/{post_id}/like
Authorization: Bearer <token>
```

### Unlike Post
```http
DELETE /posts/{post_id}/like
Authorization: Bearer <token>
```

### Save Post
```http
POST /posts/{post_id}/save
Authorization: Bearer <token>
```

### Unsave Post
```http
DELETE /posts/{post_id}/save
Authorization: Bearer <token>
```

---

## 💬 Comments

### Add Comment
```http
POST /posts/{post_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "This really resonates with me. Thank you!"
}
```

### Get Comments
```http
GET /posts/{post_id}/comments
Authorization: Bearer <token>
```

---

## 📧 Messaging

### Send First Message (Worshipers Only)
```http
POST /leaders/{leader_id}/messages
Authorization: Bearer <worshiper-token>
Content-Type: application/json

{
  "content_text": "I need guidance about prayer and meditation"
}
```

### Send Message in Chat
```http
POST /chats/{chat_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_text": "Thank you for your guidance, Pastor"
}
```

### View Conversation
```http
GET /chats/{chat_id}
Authorization: Bearer <token>
```

### Leader Inbox (All Conversations)
```http
GET /leaders/chats
Authorization: Bearer <leader-token>
```

### Worshiper Chats List
```http
GET /chats
Authorization: Bearer <worshiper-token>
```

---

## 🔔 Notifications

### Get Notifications
```http
GET /notifications?limit=50&include_read=true
Authorization: Bearer <token>

Response: {
  "notifications": [...],
  "total": 10,
  "unread_count": 3
}
```

### Mark as Read
```http
POST /notifications/{notification_id}/read
Authorization: Bearer <token>
```

### Mark All as Read
```http
POST /notifications/read-all
Authorization: Bearer <token>

Response: {
  "success": true,
  "marked_count": 5
}
```

---

## 🎯 Notification Types

### New Follower
- **Trigger**: Worshiper follows leader
- **Recipient**: Leader
- **Message**: "{Name} started following you"

### New Post
- **Trigger**: Leader publishes post
- **Recipient**: All followers
- **Message**: "{Leader} shared new spiritual content"
- **Reference**: post_id

### New Message
- **Trigger**: Message sent in chat
- **Recipient**: Other participant
- **Message**: "{Name} sent you a message"
- **Reference**: chat_id

### Question Answered
- **Trigger**: Leader answers question
- **Recipient**: Worshiper
- **Message**: "{Leader} answered your question"
- **Reference**: question_id

---

## 📊 Response Formats

### Success Response (200/201)
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2026-01-09T10:30:00Z"
}
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Error message explaining what went wrong"
}
```

### List Response
```json
{
  "items": [...],
  "total": 10,
  "offset": 0,
  "limit": 20
}
```

---

## 🚦 HTTP Status Codes

- **200** OK - Request succeeded
- **201** Created - Resource created successfully
- **400** Bad Request - Invalid input data
- **401** Unauthorized - Missing or invalid token
- **403** Forbidden - Insufficient permissions
- **404** Not Found - Resource doesn't exist
- **500** Internal Server Error - Server error

---

## 🎨 Data Validation Rules

### Email
- Must be valid email format
- Must be unique

### Password
- Minimum 8 characters
- Required on register

### Text Fields
- **Post content**: 1-5000 characters
- **Comment**: 1-1000 characters
- **Message**: 1-2000 characters
- **Question**: 10-1000 characters
- **Answer**: 10-5000 characters

### Role Values
- `worshiper` - Regular user seeking guidance
- `leader` - Spiritual leader providing guidance

---

## 🔧 Common Query Parameters

### Pagination
```
?limit=20&offset=0
```
- **limit**: Number of items to return (default: 20, max: 100)
- **offset**: Number of items to skip (default: 0)

### Filters
```
?include_read=true
```
- Used in notifications endpoint to include/exclude read items

---

## 💡 Tips for Developers

### Testing with cURL
```bash
# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Use token
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

### Testing with Postman
1. Import OpenAPI spec from `/docs`
2. Set `Authorization` header globally
3. Use environment variables for tokens

### Testing with Python
```python
import requests

# Login
response = requests.post("http://127.0.0.1:8000/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://127.0.0.1:8000/notifications", headers=headers)
print(response.json())
```

---

## 🎓 Interactive Learning

Visit the interactive API documentation:
```
http://127.0.0.1:8000/docs
```

Features:
- ✅ Try all endpoints directly in browser
- ✅ See request/response schemas
- ✅ Automatic token management
- ✅ Example values
- ✅ Error responses

---

## 📱 Mobile Integration Example (Flutter/Dart)

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class FaithConnectAPI {
  final String baseUrl = 'http://127.0.0.1:8000';
  String? _token;

  Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['access_token'];
    }
  }

  Future<List<dynamic>> getNotifications() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications'),
      headers: {'Authorization': 'Bearer $_token'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['notifications'];
    }
    return [];
  }
}
```

---

**Last Updated**: January 9, 2026  
**API Version**: 1.0.0  
**Server**: http://127.0.0.1:8000  
**Docs**: http://127.0.0.1:8000/docs
