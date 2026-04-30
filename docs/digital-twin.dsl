workspace "digital-twin-app" "Digital twin app for predict humidity based on temparature reading from sensor" {
    model {
        # Actors -> person <user-name> <description> <tag>
        user = person "User" "Digital-Twin User" "user"
        admin = person "Admin" "Digital-Twin Admin" "user"

        # Exernal Systems -> 
        sensorSystem = softwareSystem "TempSensor" "Temparature Sensor" "external"

        # Internal System
        digitaltwinSystem = softwareSystem "DigitalTwinApp" "Digital Twin System" {
            dtUIContainer = container "UI" "Digital Twin Web Page" "Streamlit / Web App" "frontend"
            dtAPIContainer = container "API Gateway" "Digital Twin FAST API Service" "FastAPI / Python" \
            "backend" {
                routerComp = component "Router" "API Router" "python"
                readingsAPIComp = component "Readings API" "API services for readings" "python"
                eventPublisherComp = component "Event Publisher" "Sensor Data Event Publisher" "python"
                dbComp = component "DBHandler" "SQLiteDatabase service handler" "python"
            }
            dtSensorContainer = container "Sensor Service" "Digital Twin Sensor Server Service" \
            "Python" "backend"
            dtProcessEventContainer = container "ProcessEvent Service" "Digital Twin Consumer Event Service" \
            "Python" "backend" {
                eventConsumerComp = component "Event Consumer" "Sensor Data Event Consumer" "python"
            }
            dtDBContainer = container "DB" "Digital Twin DB Service" "SQLite" "database"
            dtMessagingContainer = container "RabbitMQ" "RabbitMQ event management service" "RabbitMQ" "eventSystem"
        }

        # relationships between people and software systems
        user -> digitaltwinSystem "Views temparature and humidity data in dashboard"
        admin -> digitaltwinSystem "Views temparature and humidity data in dashboard"
        digitaltwinSystem -> sensorSystem "reads the temparature sensor data"

        # relationships to/from containers
        user -> dtUIContainer "Visits dt-frontend.local using HTTP" {
            tags "Logical"
        }
        admin -> dtUIContainer "Visits dt-frontend.local using HTTP" {
            tags "Logical"
        }

        dtUIContainer -> dtAPIContainer "Calls GET /readings API" {
           tags "Logical"
        }

        dtAPIContainer -> dtDBContainer "Uses CRUD operations with sensor data"
        dtAPIContainer -> dtMessagingContainer "Publishes the sensor data into RabbitMQ" {
           tags "Logical"
        }

        dtSensorContainer -> dtAPIContainer "Calls POST /readings API"
        dtSensorContainer -> sensorSystem "Reads the temparature sensor data"

        dtProcessEventContainer -> dtMessagingContainer "Processes sensor data event from RabbitMQ" {
           tags "Logical"
        }
        dtProcessEventContainer -> dtDBContainer "Stores sensor data"

        # relationships to/from components
        routerComp -> readingsAPIComp "Uses"
        
        deploymentEnvironment "Homelab" {
            mac = deploymentNode "Mac" "User machine" "macOS" {
                browser = infrastructureNode "Web Browser" "Chrome / Safari"
            }

            raspberrypi = deploymentNode "Raspberry Pi" "Single-node K3s server" "Raspberry Pi OS / Linux" {
                    
                k3s = deploymentNode "K3s Cluster" "Lightweight Kubernetes cluster" "K3s" {

                    ingress = infrastructureNode "Traefik Ingress" "Exposes services to Mac browser"

                    frontendNamespace = deploymentNode "default" "digital twin apps namespace" {
                        frontendService = infrastructureNode "frontend-service" "Kubernetes Service"
                        frontendPod = deploymentNode "frontend-pod" "Kubernetes Pod" {
                            frontendInstance = containerInstance dtUIContainer
                        }
                        backendService = infrastructureNode "backend-service" "Kubernetes Service"
                        backendPod = deploymentNode "backend-pod" "Kubernetes Pod" {
                            apiInstance = containerInstance dtAPIContainer
                            consumerInstance = containerInstance dtProcessEventContainer
                            sensorInstance = containerInstance dtSensorContainer

                            sqlite = infrastructureNode "SQLite DB File" "Stored inside container filesystem or volume"
                        }
                    }

                    messagingNamespace = deploymentNode "messaging" "messaging namespace" {
                        rabbitmqService = infrastructureNode "rabbitmq-service" "Kubernetes Service"
                        rabbitmqPod = deploymentNode "rabbitmq-pod" "Kubernetes Pod" {
                            rabbitmqInstance = containerInstance dtMessagingContainer
                        }
                    }
                }

            sensor = deploymentNode "Hardware System" "" "Hardware" {
                sensorNode = infrastructureNode "Sensor" "IOT"
                }
            }

            browser -> ingress "HTTP/HTTPS"
            ingress -> frontendService "Routes traffic"
            frontendService -> frontendInstance "Forwards requests"

            frontendInstance -> backendService "HTTP REST API"
            backendService -> apiInstance "Forwards requests"

            apiInstance -> rabbitmqService "publish the request"
            rabbitmqService -> rabbitmqInstance "Forwards messages"
            consumerInstance -> rabbitmqService "Consumes the request"
            consumerInstance -> sqlite "adds the sensor data"

            sensorInstance -> sensorNode "Reads the temparature data"
            sensorInstance -> backendService "Sends the temparature and humidity data"

            apiInstance -> sqlite "creates, reads, puts or delete sensor data"
        }
    }    

    # Views
    views {
        systemlandscape "SystemLandscape" {
            include *
            autoLayout
        }            

        systemcontext digitaltwinSystem "SystemContext" {
            include *
            animation {
                digitaltwinSystem
                user
                sensorSystem
            }
            autoLayout
        }

        container digitaltwinSystem "Containers" {
            include *
            animation {
                user sensorSystem
                dtUIContainer
                dtSensorContainer
                dtProcessEventContainer
                dtDBContainer
                dtMessagingContainer
            }
            autoLayout
        }

        component dtAPIContainer "Components" {
            include *
            autoLayout
        }

        dynamic digitaltwinSystem "DigitalTwinFlow" {
            title "Showing dashboard with values of Humidity and Temparature Workflow"

            user -> dtUIContainer "Opens UI"
            dtUIContainer -> dtAPIContainer "GET /readings"
            dtAPIContainer -> dtDBContainer "reads sensor data"
            dtAPIContainer -> dtUIContainer "returns sensor data"
            dtUIContainer -> user "shows data in dashboard"
        }        

        dynamic digitaltwinSystem "ReadSensorDataFlow" {
            title "Read sensor data and add to database workflow"

            dtSensorContainer -> sensorSystem "Reads the temparature sensor data"
            dtSensorContainer -> dtAPIContainer "Calls POST /readings API"
            dtAPIContainer -> dtMessagingContainer "Publishes the sensor data into RabbitMQ"
            dtProcessEventContainer -> dtMessagingContainer "Processes sensor data event from RabbitMQ"
            dtProcessEventContainer -> dtDBContainer "Stores sensor data"
        }

        deployment digitaltwinSystem "Homelab" "HomelabDeployment" {
            include *

            exclude "relationship.tag==Logical"

            autolayout lr
        }                
    }
}