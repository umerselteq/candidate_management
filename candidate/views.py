from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Candidate, CandidateStatus
from .serializers import CandidateSerializer, CandidateStatusSerializer
from django.http import Http404
from django.core.cache import cache
from django.http import JsonResponse

def cache_view(request):
    data = cache.get('my_key')
    if not data:
        # Compute the data
        data = 'some expensive computation'
        cache.set('my_key', data, timeout=60*15)  # Cache for 1 minutes
        #return JsonResponse("data here:", data)
    return JsonResponse({'data': data})


class CandidateSetByParent(APIView):
    def get(self, request):
        parent_id = request.GET.get('parent_id')
        try:
            candidates = Candidate.objects.filter(parentId=parent_id)
            if candidates is not None:
                serializer = CandidateSerializer(candidates, many=True)
                return Response(serializer.data)
            else:
                return Response({'error': 'No candidates found against this parent'}, status=status.HTTP_404_NOT_FOUND)
        except Candidate.DoesNotExist:
            raise Http404
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        responses = []
        errors = []
        try:
            candidates = setting_parent_id(request)
            if candidates is None:
                return Response({'error': 'multiple candidates provided but no parent id'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        for candidate in candidates:
            try:
                serializer = CandidateSerializer(data=candidate)
                if serializer.is_valid():
                    c = serializer.save()
                    responses.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            except Exception as e:
                errors.append({'error': str(e)})

        if errors:
            return Response({'success': responses, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': responses}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        parent_id = request.GET.get('parent_id')
        try:
            candidates = Candidate.objects.filter(parentId=parent_id)
            candidates.delete()
            return Response({'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


# class CandidateViewSet(APIView):
#     def get(self, request):
#         try:
#             candidates = Candidate.objects.all()
#             serializer = CandidateSerializer(candidates, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#     def post(self, request):
#         responses = []
#         errors = []
#         for data in request.data:
#             try:
#                 serializer = CandidateSerializer(data=data)
#                 if serializer.is_valid():
#                     c = serializer.save()
#                     responses.append(serializer.data)
#                 else:
#                     errors.append(serializer.errors)
#             except Exception as e:
#                 errors.append({'error': str(e)})
#
#         if errors:
#             return Response({'success': responses, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({'success': responses}, status=status.HTTP_201_CREATED)




class CandidateViewSet_By_Id(APIView):
    def get_object(self, pk):
        try:
            return Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            raise Http404

    def get(self, request):
        id = self.request.query_params.get('id', None)
        print(id)
        if id is None:
            try:
                candidates = Candidate.objects.all()
                serializer = CandidateSerializer(candidates, many=True)
                return Response(serializer.data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                c = self.get_object(id)
                serializer = CandidateSerializer(c)
                return Response(serializer.data)
            except Http404:
                return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        responses = []
        errors = []
        for data in request.data:
            try:
                serializer = CandidateSerializer(data=data)
                if serializer.is_valid():
                    c = serializer.save()
                    responses.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            except Exception as e:
                errors.append({'error': str(e)})

        if errors:
            return Response({'success': responses, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': responses}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        id = self.request.query_params.get('id', None)
        try:
            c = self.get_object(id)
            c.delete()
            return Response({'success': True})
        except Http404:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        id = self.request.query_params.get('id', None)
        try:
            c = self.get_object(id)
            serializer = CandidateSerializer(c, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CandidateStatusViewSet(APIView):
    def get(self, request):
        try:
            #data = cache.get('my_key') for redis checking
            candidates = CandidateStatus.objects.all()
            serializer = CandidateStatusSerializer(candidates, many=True)
            return Response(serializer.data)
            #return JsonResponse({'data': data}) for redis checking
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            serializer = CandidateStatusSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        candidate_id = self.request.query_params.get('candidate_id', None)
        if candidate_id is None:
            return Response({'error': 'provide candidate id'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return self.change_candidate_status(request, candidate_id)

    def change_candidate_status(self, request, candidate_id):
        try:
            c = CandidateStatus.objects.get(candidateId=candidate_id)
            serializer = CandidateStatusSerializer(c, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def setting_parent_id(request):
    parent_id = request.data.get("parentId", None)
    candidates = request.data.get("candidates", None)
    length = len(candidates)
    print(length)
    if length == 1:
        return candidates
    if length > 1:
        if parent_id is None:
            print({'error': 'multiple candidates provided but no parent id'})
            return None
        for candidate in candidates:
            candidate['parentId'] = parent_id
        return candidates


# def create_status(r):
#     try:
#         data = {'candidateId': r}
#         print("id in status:", data)
#         serializer = CandidateStatusSerializer(data=data)
#         if serializer.is_valid():
#             s = serializer.save()
#             print("status created:", s)
#         else:
#             print("status error:", serializer.errors)
#     except Exception as e:
#         print(e)


