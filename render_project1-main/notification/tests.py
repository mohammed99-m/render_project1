# from django.test import TestCase
# from unittest.mock import patch
# from rest_framework import status
# from rest_framework.test import APIClient
# import requests 

# class NotificationAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = '/notification/send_notification/'  # استبدل هذا بالمسار الصحيح

#     @patch('notification.views.requests.post')  # استبدل 'your_app_name' باسم تطبيقك
#     def test_send_notification_success(self, mock_post):
#         # إعداد mock ليرد بنجاح
#         mock_post.return_value.status_code = 200

#         # بيانات الاختبار
#         payload = {
#             'message': 'Test notification',
#             'user_id': 1  # استخدم معرف مستخدم صحيح هنا
#         }

#         response = self.client.post(self.url, payload)

#         # تحقق من أن الاستجابة صحيحة
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, {"message": "Notification sent successfully"})

#     @patch('notification.views.requests.post')  # استبدل 'your_app_name' باسم تطبيقك
#     def test_send_notification_failure(self, mock_post):
#         # إعداد mock ليرد بفشل
#         mock_post.return_value.status_code = 500

#         # بيانات الاختبار
#         payload = {
#             'message': 'Test notification',
#             'user_id': 1  # استخدم معرف مستخدم صحيح هنا
#         }

#         response = self.client.post(self.url, payload)

#         # تحقق من أن الاستجابة صحيحة
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(response.data, {"message": "Failed to send notification"})