import json
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from dry_rest_permissions.generics import DRYPermissions

from users.models import User
from users.serializers import UserSerializer

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class UserViewSet(ModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['GET'])
    def get_users(self, request):
        users = User.objects.filter(is_active = True).order_by('id').values('id', 'username')

        return Response(
            {'users': users},
            status=200
        )
    
    @action(detail=False, methods=['POST'])
    def register(self, request):
        user_exist = User.objects.filter(Q(email=request.data['email']) | Q(username=request.data['username'])).first()

        if not user_exist:
            serializer = self.serializer_class(data = request.data)
            
            if serializer.is_valid():
                user = User.objects.create_user(**serializer.validated_data)
                return Response(status=200)
            
            return Response(
                data='入力した情報が正しくありません。',
                status=400
            )
        else:
            return Response(
                data='同じメールを持つユーザーが既に存在します。',
                status=400
            )
    
    @action(detail=False, methods=['POST'])
    def login(self, request):
        # user = User.objects.filter(email=request.data['email']).first()
        user = authenticate(request=request, email=request.data['email'], password=request.data['password'])

        # user = authenticate(request=request, username=request.data['username'], password=request.data['password'])
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            data = {
                'token': token.key,
                'user': self.serializer_class(user).data
            }

            if data['user']['is_active'] == True:
                return Response(
                    data=data,
                    status=200
                )
            else:
                return Response(
                    data = 'ログイン要求が承認されるまでお待ちください。',
                    status = 401
                )
        else:
            return Response(
                data='メールやパスワードが正しくありません。',
                status=401
            )

    def update(self, request, *args, **kwargs):
        data = request.data
        
        with open(file=str(settings.BASE_DIR / 'utils/ebay_settings.txt'),  mode='w', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=4))

        serializer = self.serializer_class(instance=request.user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data='Success',
                status=200
            )
        
    @action(detail=False, methods=['GET'])
    def get_userlist(self, request):
        perPageNum = request.GET.get('pageSize')
        page = request.GET.get('page')

        user_list = []

        user_list = User.objects.filter(is_active = True, is_superuser = False).order_by('id').values('id', 'username', 'date_joined', 'email', 'is_active')

        paginator = Paginator(user_list, perPageNum)

        try:
            users = paginator.page(page).object_list
        except PageNotAnInteger:
            users = paginator.page(1).object_list
        except EmptyPage:
            users = paginator.page(paginator.num_pages).object_list

        return Response({'count': paginator.count, 'users': users.values()}, status = 200)
    
    @action(detail=False, methods=['GET'])
    def get_deactive_userlist(self, request):
        perPageNum = request.GET.get('pageSize')
        page = request.GET.get('page')

        user_list = []

        user_list = User.objects.filter(is_active = False).order_by('id').values('id', 'username', 'date_joined', 'email', 'is_active')

        paginator = Paginator(user_list, perPageNum)

        try:
            users = paginator.page(page).object_list
        except PageNotAnInteger:
            users = paginator.page(1).object_list
        except EmptyPage:
            users = paginator.page(paginator.num_pages).object_list

        return Response({'count': paginator.count, 'users': users.values()}, status = 200)
        
    @action(detail=False, methods=['POST'])
    def allow_user(self, request):
        user_id = request.data['user_id']
        allow = request.data['allow']

        try:
            User.objects.filter(id = user_id).update(is_active=allow)

            return Response(
                data = '操作に成功しました！',
                status = 200
            )
        except:
            return Response(
                data = '操作が失敗しました！',
                status = 401
            )
        
    @action(detail=False, methods=['POST'])
    def delete_user(self, request):
        user_id = request.data['userid']

        try:
            User.objects.filter(id = user_id).delete()

            return Response(
                data = 'ユーザー情報を削除しました！',
                status = 200
            )
        except:
            return Response(
                data = 'ユーザー削除作業が失敗しました！',
                status = 401
            )

    @action(detail=False, methods=['GET'])
    def get_ebay_info(self, request):
        serializer = self.serializer_class(request.user).data
        data = {
            'app_id': serializer['app_id'] or '',
            'dev_id': serializer['dev_id'] or '',
            'cert_id': serializer['cert_id'] or '',
            'ebay_token': serializer['ebay_token'] or '',
        }
        return Response(
            data=data,
            status=200
        )

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response(
            data='Success',
            status=200
        )
