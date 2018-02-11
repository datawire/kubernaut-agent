# Kubernaut Agent

Kubernaut agent is a tiny agent that registers and heartbeats the existence of a Kubernetes cluster to the Kubernaut controller. 

The Kubernaut agent is intended to run as a sibling process to the `kubelet`, but it can also be run as a pod on a Kubernetes cluster as well. Care must be taken when running the agent as a pod in Kubernetes to ensure that it is not deleted otherwise the agent and controller are unable to communicate with each other.

The agent communicates with the controller using a bidirectional adhoc JSON web socket protocol which is known as the Cluster Agent Protocol v1 or CAPv1. The CAP is designed to support multi-cluster communication from a single agent, but the current Kubernaut Agent does not support multiple cluster registration and heartbeating.

# Cluster Identity

Establishing cluster identity in Kubernetes is difficult because there is no official mechanism to find a unique and deterministic cluster identifier built into Kubernetes. Until such a feature exists, the Kubernaut agent relies on the `UID` of the `default` namespace in Kubernetes. The `default` namespace is special in that it cannot be deleted. Therefore, two clusters are distinct from the view of the controller if the `UID` of the `default` namespace in each cluster is unique.

# Agent Identifier 

Each agent has a unique identifier. The ID is a UUID and it stored in `$HOME/.config/kubernaut-agent/id`. When the agent starts the `id` file is read but if the `id` file does not exist or is empty then it is created and populated.

The agent identifier exists primarily to allow the controller to associate one or more clusters to an agent and if the agent disconnects when the agent reconnects the controller can sync any change of state to the agent which can then take appropriate action.

# Startup Process

When the agent starts the following things occur:

1. The agent ID is read or created.
2. A web socket connection is opened with the Kubernaut Controller.
3. The agent sends a `sync-request` message to the server with its agent ID.

    ```json
    {
      "@type": "sync-request",
      "agentId": "__AGENT_ID__"
    }
    ```

4. The server responds with a `sync-response` message to agent. The `sync-response` message will contain information, if any exists, about the status of a claim associated with a cluster. If the controller is not aware of any clusters associated with an agent then the `clusters` array is empty.

    ```json
    {
      "@type": "sync-response",
      "agentId": "__AGENT_ID__",
      "clusters": {
        "__CLUSTER_ID__": {"status": "UNCLAIMED|CLAIMED|DISCARDED"}
      }
    }
    ```

# Cluster Registration Handshake

If the `sync-response` message is empty then the agent can send its cluster to the controller for registration:

    ```json
    {
      "@type": "cluster-registration-request",
      "agentId": "__AGENT_ID__",
      "clusters": {
        "__CLUSTER_ID__": "__CLUSTER_KUBECONFIG__"
      }
    }
    ```

The controller then sends back a response:

    ```json
    {
      "@type": "cluster-registration-response",
      "agentId": "__AGENT_ID__",
      "clusters": {
        "__CLUSTER_ID__": {"status": "ACCEPTED|REJECTED"}
      }
    }
    ```

For each `ACCEPTED` registration the agent needs to send periodic heartbeats to the controller to indicate the clusters are still available to be claimed. These messages are very simple:

    ```json
    {
      "@type": "cluster-heartbeat",
      "agentId": "__AGENT_ID__",
      "clusters": ["__CLUSTER_ID__"]
    }
    ```

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
