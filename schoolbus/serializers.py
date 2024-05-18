from rest_framework import serializers
from schoolbus.models import Bus , BusPoint , Route






class BusRouteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BusPoint
        fields = ['route','name','fee']

    
    
class RouteSerializer(serializers.ModelSerializer):
    bus_points = BusRouteSerializer(many=True,read_only=True)
    
    class Meta:
        model = Route
        fields = ['id','bus','route_no','from_location','to_location','bus_points']
        
        
    def update(self, instance, validated_data):
        instance.bus = validated_data.get('bus',instance.bus)
        instance.route_no = validated_data.get('route_no',instance.route_no)
        instance.from_location = validated_data.get('from_location',instance.from_location)
        instance.to_location = validated_data.get('to_location',instance.to_location)
        
        instance.save()
        return instance
    
    
    
class BusSerializer(serializers.ModelSerializer):
    routes = RouteSerializer(many=True,read_only=True)
    
    
    class Meta:
        model = Bus
        fields = ['id','bus_no','driver_name','plate_number','capacity','routes']
        
        
    def update(self, instance, validated_data):
        instance.bus_no = validated_data.get('bus_no',instance.bus_no)
        instance.driver_name = validated_data.get('driver_name',instance.driver_name)
        instance.plate_number = validated_data.get('plate_number',instance.plate_number)
        instance.capacity = validated_data.get('capacity',instance.capacity)
        
        instance.save()
        return instance