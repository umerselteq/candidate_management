from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Candidate, CandidateStatus
from .serializers import CandidateSerializer, CandidateStatusSerializer
from django.http import Http404
from django.core.cache import cache
from django.http import JsonResponse
from candidate.throttling import CustomRateThrottle
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle



class login(APIView):
    def post(self, request):
        try:
            candidate_id = request.data['candidate_id']
            data = cache.get('candidates')
            if data is None:
                data = candidate_cache_set()
            for candidate in data:
                if candidate['id'] == candidate_id:
                    cache.set('id', candidate['id'], timeout=60 * 15)
                    return Response({'id': candidate_id}, status=status.HTTP_200_OK)
            else:
                return Response({'id': candidate_id}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)})


def cache_view(request):
    data = cache.get('my_key')
    if not data:
        data = 'some expensive computation'
        cache.set('my_key', data, timeout=60*15)
    return JsonResponse(data, safe=False)


def candidate_cache_set():
    try:
        print("candidate cache called")
        data = Candidate.objects.all()
        serializer = CandidateSerializer(data, many=True)
        serialized_data = serializer.data
        cache.set('candidates', serialized_data, timeout=60*15)
        return serialized_data
    except Exception as e:
        print(e)


class CandidateSetByParent(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        parent_id = request.GET.get('parent_id')
        parent_id = int(parent_id)
        try:
            data = cache.get('candidates')
            if data is None:
                data = candidate_cache_set()
            candidates = data
            persons = [candidate for candidate in candidates if candidate.get('parentId') == parent_id]
            return JsonResponse(persons, safe=False)
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
                return Response({'error': 'multiple candidates but no parent id'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        for candidate in candidates:
            try:
                serializer = CandidateSerializer(data=candidate)
                if serializer.is_valid():
                    serializer.save()
                    responses.append(serializer.data)
                    candidate_cache_set()
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
            candidate_cache_set()
            return Response({'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class CandidateViewSet_By_Id(APIView):
    def get_object(self, pk):
        try:
            return Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            raise Http404

    # only login users
    def get(self, request):
        user_id = self.request.query_params.get('id', None)
        if user_id is None:
            self.throttle_classes = [AnonRateThrottle]
        else:
            self.throttle_classes = [UserRateThrottle]
        self.check_throttles(request)

        if user_id is None:
            try:
                data = cache.get('candidates')
                if not data:
                    data = candidate_cache_set()
                return JsonResponse(data, safe=False)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if user_id:
            user_id = int(user_id)
            logged = cache.get('id')
            if logged is None:
                print("no logged")
                return Response({'logged': 'cache timeout logged user'}, status=status.HTTP_404_NOT_FOUND)
            if user_id != logged:
                return Response({'not a authenticated user'}, status=status.HTTP_401_UNAUTHORIZED)
            print(user_id)
            try:
                data = cache.get('candidates')
                if not data:
                    data = candidate_cache_set()
                candidates = data
                for candidate in candidates:
                    if candidate['id'] == user_id:
                        return JsonResponse(candidate, safe=False)
                else:
                    return JsonResponse({'no candidate with id:': user_id}, safe=False)
            except Http404:
                return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_id = self.request.query_params.get('id', None)
        try:
            c = self.get_object(user_id)
            c.delete()
            candidate_cache_set()  # update the cache
            return Response({'success': True})
        except Http404:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user_id = self.request.query_params.get('id', None)
        try:
            c = self.get_object(user_id)
            serializer = CandidateSerializer(c, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                candidate_cache_set()  # update the cache
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CandidateStatusViewSet(APIView):
    def get(self, request):
        try:
            data = cache.get('candidates')
            if not data:
                data = candidate_cache_set()
            candidates = data
            persons = [(candidate['id'], candidate['firstName'], candidate['status']) for candidate in candidates]
            # persons.append((candidate['id'], candidate['firstName'], candidate['status']))
            return JsonResponse(persons, safe=False)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            serializer = CandidateStatusSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                candidate_cache_set()
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
                candidate_cache_set()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def setting_parent_id(request):
    try:
        parent_id = request.GET.get('parent_id', None)
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
    except Exception as e:
        print({'error': str(e)})
