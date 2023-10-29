from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def create_relation(request, model, model_relation, pk, serializer, field):
    "Функция создания связи User -> Model."

    model_obj = get_object_or_404(model, pk=pk)
    model_relation_obj = model_relation.objects.filter(
        client=request.user, **{field: model_obj}
    )

    if not model_relation_obj.exists():
        model_relation.objects.create(client=request.user,
                                      **{field: model_obj})
        serializer = serializer(model_obj, context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)
    return Response(
        data={'errors': 'Попытка повторного добавления объекта'},
        status=status.HTTP_400_BAD_REQUEST
    )


def delete_relation(request, model, model_relation, pk, field):
    "Функция удаления связи User -> Model."

    model_obj = get_object_or_404(model, pk=pk)
    model_relation_obj = model_relation.objects.filter(
        client=request.user, **{field: model_obj}
    )

    if model_relation_obj.exists():
        model_relation_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        data={'errors': 'Попытка удаления несуществующего объекта'},
        status=status.HTTP_404_NOT_FOUND
    )


def get_validated_field(values, model):
    "Вспомогательная функция валидации полей."

    if values:
        check_list = []
        for elem_id in values:
            if not model.objects.filter(id=elem_id).exists():
                raise ValidationError('Несуществующий элемент!')
            if elem_id in check_list:
                raise ValidationError(
                    'Повторное добавление элемента!'
                )
            check_list.append(elem_id)
    else:
        raise ValidationError(
            'Необходимо указать минимум один элемент!'
        )

    return values
