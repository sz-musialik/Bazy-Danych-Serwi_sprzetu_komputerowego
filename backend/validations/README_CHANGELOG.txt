Validation and service mapping notes:
- AuthService.create_user -> backend/utils/auth_service.py
- UserService.create_user/set_archived/assign_role -> backend/services/user_service.py
- ClientService.create_client/update_client/deactivate_client -> backend/services/client_service.py
- OrderService.create_order/change_status -> backend/services/order_service.py
- PartsService.add_part/update_part/update_stock -> backend/services/parts_service.py
- PartsUsedService.add_used_part/list_used_parts -> backend/services/parts_used_service.py
- PartsOrderService.create_order/add_item/change_status -> backend/services/parts_order_service.py
- Validations live in backend/validations/output_validators.py

