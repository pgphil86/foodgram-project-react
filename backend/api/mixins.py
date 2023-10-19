from rest_framework import mixins, viewsets


class CreateAndDeleteViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    '''
    Mixin for creating and deleting.
    '''

    pass


class ListViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''
    Mixin for get some list.
    '''

    pass
