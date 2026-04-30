workspace "digital-twin-app" "Digital twin app for predict humidity based on temparature reading from sensor" {
    model {
        # Actors -> person <user-name> <description> <tag>
        user = person "User" "Digital-Twin User" "user"
        admin = person "Admin" "Digital-Twin Admin" "user"

        # Exernal Systems
        sensorSystem = softwareSystem "TempSensor" "Temparature Sensor" "external"

        # Internal System
        digitaltwinSystem = softwareSystem "DigitalTwinApp" "Digital Twin System" {
            
            frontendContainer = container "UI" "Digital Twin Web Page" "Streamlit / Web App" "frontendContainer"
            
            backendContainer = container "Backend Service" "DT Backend Services" "Python" "backendContainer" {
                apiComponent = component "API Gateway" "Digital Twin FAST API Service" "FastAPI / Python" \
                "backendContainer" 
                sensorComponent = component "Sensor Service" "Digital Twin Sensor Server Service" \
                "Python" "backendContainer"
                consumerComponent = component "ProcessEvent Service" "Digital Twin Consumer Event Service" \
                "Python" "backendContainer"
            }
            
            sqliteContainer = container "SQLite" "SQLite Database" "SQLite" "database"            
            messageContainer = container "RabbitMQ" "RabbitMQ event management service" "RabbitMQ" "eventSystem"
            
            # relationships between people and software systems
            user -> digitaltwinSystem "Views temparature and humidity data in dashboard"
            admin -> digitaltwinSystem "Views temparature and humidity data in dashboard"
            digitaltwinSystem -> sensorSystem "reads the temparature sensor data"

            # relationships to/from containers
            user -> frontendContainer "Visits dt-frontendContainer.local using HTTP" {
                tags "Logical"
            }
            admin -> frontendContainer "Visits dt-frontendContainer.local using HTTP" {
                tags "Logical"
            }

            frontendContainer -> apiComponent "Calls GET /readings API" {
                tags "Logical"
            }

            apiComponent -> sqliteContainer "Uses CRUD operations with sensor data"
            apiComponent -> messageContainer "Publishes the sensor data into RabbitMQ" {
                tags "Logical"
            }

            sensorComponent -> sensorSystem "Reads the temparature sensor data"

            consumerComponent -> messageContainer "Processes sensor data event from RabbitMQ" {
                tags "Logical"
            }
            consumerComponent -> sqliteContainer "Stores sensor data"

            # relationships to/from components
            sensorComponent -> apiComponent "Calls POST /readings API"
        }

        # Logging System
        loggingSystem = softwareSystem "Logging" "Logging System" {
            
            lokiContainer = container "Loki" "Log aggregation backendContainer" "Loki"
            fluentbitContainer = container "Fluent Bit" "Collects and forwards container logs" "Fluent Bit"

            # relationships to/from containers
            frontendContainer -> fluentbitContainer "Writes logs"
            apiComponent -> fluentbitContainer "Writes logs"
            sensorComponent -> fluentbitContainer "Writes logs"
            consumerComponent -> fluentbitContainer "Writes logs"

            fluentbitContainer -> lokiContainer "Ships logs"
        }

        # Monitoring System
        monitoringSystem = softwareSystem "Monitoring" "Observability Tools" {

            grafanaSystem = container "Grafana Web App" "Dashboards" "Docker / Web App"
            prometheusSystem = container "Prometheus" "Metrics" "Docker / Web App"
            rancherSystem = container "Rancher Web browser" "K8s management" "HTTP"

            # relationships between people and software systems
            admin -> grafanaSystem "Views dashboards"
            admin -> rancherSystem "Manages cluster"

            # relationships to/from containers
            frontendContainer -> prometheusSystem "Exposes /metrics" {
                tags "Logical"
            }
            sensorComponent -> prometheusSystem "Exposes /metrics" {
                tags "Logical"
            }
            apiComponent -> prometheusSystem "Exposes /metrics" {
                tags "Logical"
            }
            consumerComponent -> prometheusSystem "Exposes /metrics" {
                tags "Logical"
            }

            grafanaSystem -> prometheusSystem "Queries metrics"
            grafanaSystem -> lokiContainer "Queries logs"
        }

        deploymentEnvironment "Homelab" {
            mac = deploymentNode "Mac" "User machine" "macOS" {
                browser = infrastructureNode "Web Browser" "Chrome / Safari"

                grafanaDeployment = infrastructureNode "Grafana" "Grafana Web Application" "Docker"

                prometheusMasterDeployment = deploymentNode "Prometheus" "Prometheus Master" "Docker"

                rancherUI = infrastructureNode "Rancher UI" "Chrome / Safari" "HTTP"
   
            }

            raspberrypi = deploymentNode "Raspberry Pi" "Single-node K3s server" "Raspberry Pi OS / Linux" {
                    
                k3s = deploymentNode "K3s Cluster" "Lightweight Kubernetes cluster" "K3s" {

                    ingress = infrastructureNode "Traefik Ingress" "Exposes services to Mac browser"

                    frontendContainerNamespace = deploymentNode "default" "digital twin apps namespace" {
                        frontendContainerService = infrastructureNode "frontendContainer-service" "Kubernetes Service"
                        frontendContainerPod = deploymentNode "frontendContainer-pod" "Kubernetes Pod" {
                            frontendContainerInstance = containerInstance frontendContainer
                        }
                        backendContainerService = infrastructureNode "backendContainer-service" "Kubernetes Service"
                        backendContainerPod = deploymentNode "backendContainer-pod" "Kubernetes Pod" {
                            backendInstance = containerInstance backendContainer

                            sqlite = infrastructureNode "SQLite DB File" "Stored inside container filesystem or volume"
                        }
                    }

                    messagingNamespace = deploymentNode "messaging" "messaging namespace" {
                        rabbitmqService = infrastructureNode "rabbitmq-service" "Kubernetes Service"
                        rabbitmqPod = deploymentNode "rabbitmq-pod" "Kubernetes Pod" {
                            rabbitmqInstance = containerInstance messageContainer
                        }
                    }

                    loggingNs = deploymentNode "logging" "Kubernetes namespace" {
                        lokiContainerSvc = infrastructureNode "lokiContainer-service" "Kubernetes Service"

                        lokiContainerPod = deploymentNode "lokiContainer-pod" "Kubernetes Pod" {
                            lokiContainerInstance = containerInstance lokiContainer
                        }

                        fluentbitContainerDaemonSet = deploymentNode "fluent-bit-daemonset" "Runs on each Kubernetes node" {
                            fluentbitContainerInstance = containerInstance fluentbitContainer
                        }
                    }

                    monitoringNs = deploymentNode "monitoring" "monitoring namespace"{
                        prometheusSvc = infrastructureNode "prometheus-service" "Kubernetes Service"

                        prometheusNode = deploymentNode "Prometheus (minion)" "Kubernetes Pod"{
                            prometheusMinionDeployment = containerInstance prometheusSystem
                        }
                    }

                    rancherNs = deploymentNode "cattle-system" "Kubernetes namespace" {
                        rancherSvc = infrastructureNode "rancher-service" "Kubernetes Service"

                        rancherPod = deploymentNode "rancher-pod" "Kubernetes Pod" {
                            rancherDeployment = containerInstance rancherSystem
                        }
                    }                                                            
                }

            sensor = deploymentNode "Hardware System" "" "Hardware" {
                sensorNode = infrastructureNode "Sensor" "IOT"
                }
            }

            browser -> ingress "HTTP/HTTPS"
            ingress -> frontendContainerService "Routes traffic"
            frontendContainerService -> frontendContainerInstance "Forwards requests"

            frontendContainerInstance -> backendContainerService "HTTP REST API"
            backendContainerService -> backendInstance "Forwards requests"

            backendInstance -> rabbitmqService "publish the request"
            rabbitmqService -> rabbitmqInstance "Forwards messages"
            backendInstance -> rabbitmqService "Consumes the request"
            backendInstance -> sqlite "adds the sensor data"

            backendInstance -> sensorNode "Reads the temparature data"
            backendInstance -> backendContainerService "Sends the temparature and humidity data"

            backendInstance -> sqlite "creates, reads, puts or delete sensor data"

            fluentbitContainerInstance -> lokiContainerSvc "Pushes logs"
            lokiContainerSvc -> lokiContainerInstance "Forwards queries"

            prometheusSvc -> backendInstance "Scrapes metrics"
            prometheusSvc -> frontendContainerInstance "Scrapes metrics"
            prometheusSvc -> rabbitmqInstance "Scrapes metrics"

            grafanaDeployment -> prometheusSvc "Queries metrics"
            prometheusSvc -> prometheusMinionDeployment "Forwards queries"

            grafanaDeployment -> lokiContainerSvc "Queries logs"

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
                frontendContainer
                backendContainer
                sqliteContainer
                messageContainer
            }
            autoLayout
        }

        component backendContainer "Components" {
            include *
            autoLayout
        }

        dynamic digitaltwinSystem "DigitalTwinFlow" {
            title "Showing dashboard with values of Humidity and Temparature Workflow"

            user -> frontendContainer "Opens UI"
            frontendContainer -> backendContainer "GET /readings"
            backendContainer -> sqliteContainer "reads sensor data"
            backendContainer -> frontendContainer "returns sensor data"
            frontendContainer -> user "shows data in dashboard"
        }        

        dynamic digitaltwinSystem "ReadSensorDataFlow" {
            title "Read sensor data and add to database workflow"

            backendContainer -> sensorSystem "Reads the temparature sensor data"
            backendContainer -> messageContainer "Publishes the sensor data into RabbitMQ"
            backendContainer -> messageContainer "Processes sensor data event from RabbitMQ"
            backendContainer -> sqliteContainer "Stores sensor data"
        }

        deployment digitaltwinSystem "Homelab" "HomelabDeployment" {
            include *

            exclude "relationship.tag==Logical"

            autolayout lr
        }                
    }
}