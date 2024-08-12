from rest_framework import serializers
from api.models import  Project, Task, Feedback, Status


# class UserSerializer(serializers.Serializer):
#     class Meta:
#         model = User
#         # Default to all fields


    # def create(self, validated_data):
    #     status_data_list = validated_data.pop('taskStatuses', [])
    #     project = Project(**validated_data)
    #     project.taskStatuses = []

    #     for status_data in status_data_list:
    #         project.taskStatuses.append(Project.Status(**status_data))

    #     project.save()
    #     return project
        
    # def update(self, instance, validated_data):
    #     # Extract the embedded document data
    #     status_data_list = validated_data.pop('taskStatuses', [])
        
    #     # Update the main document fields
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.types = validated_data.get('types', instance.types)
    #     instance.objectives = validated_data.get('objectives', instance.objectives)
    #     instance.startDate = validated_data.get('startDate', instance.startDate)
    #     instance.endDate = validated_data.get('endDate', instance.endDate)
    #     instance.budget = validated_data.get('budget', instance.budget)
    #     instance.assumptions = validated_data.get('assumptions', instance.assumptions)
    #     instance.scopesIncluded = validated_data.get('scopesIncluded', instance.scopesIncluded)
    #     instance.scopesExcluded = validated_data.get('scopesExcluded', instance.scopesExcluded)
    #     instance.risks = validated_data.get('risks', instance.risks)
    #     instance.profileIDs = validated_data.get('profileIDs', instance.profileIDs)
    #     instance.projectManagerIDs = validated_data.get('projectManagerIDs', instance.projectManagerIDs)
    #     instance.sponsors = validated_data.get('sponsors', instance.sponsors)
    #     instance.contributorIDs = validated_data.get('contributorIDs', instance.contributorIDs)
    #     instance.completionRequirements = validated_data.get('completionRequirements', instance.completionRequirements)
    #     instance.qualityAssurance = validated_data.get('qualityAssurance', instance.qualityAssurance)
    #     instance.KPIs = validated_data.get('KPIs', instance.KPIs)
    #     instance.otherProjectDependencies = validated_data.get('otherProjectDependencies', instance.otherProjectDependencies)
    #     instance.informationLinks = validated_data.get('informationLinks', instance.informationLinks)
    #     instance.completionStatus = validated_data.get('completionStatus', instance.completionStatus)
    #     instance.teams = validated_data.get('teams', instance.teams)
        
    #     # Clear the existing comments
    #     instance.taskStatuses = []

    #     # Add the new embedded documents to the main document
    #     for status_data in status_data_list:
    #         instance.taskStatuses.append(Project.Status(**status_data))
        
    #     # Save the main document
    #     instance.save()
    #     return instance


class TaskSerializer(serializers.Serializer):
    class Meta:
        model = Task
        # Default to all fields

class FeedbackSerializer(serializers.Serializer):
    class Meta:
        model = Feedback


class GeneratedTaskSerializer(serializers.Serializer):
    projectID = serializers.CharField(required=True)
    name = serializers.CharField(required=True)  # project name
    description = serializers.CharField(allow_blank=True, allow_null=True)
