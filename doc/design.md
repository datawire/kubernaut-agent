# Kubernaut Agent

Kubernaut agent is a tiny agent that registers and heartbeats the existence of a Kubernetes cluster to the Kubernaut controller. 

The Kubernaut agent is intended to run as a sibling process to the `kubelet`, but it can also be run as a pod on a Kubernetes cluster as well. Care must be taken when running the agent as a pod in Kubernetes to ensure that it is not deleted otherwise the agent and controller are unable to communicate with each other.

The agent communicates with the controller using a bidirectional adhoc JSON web socket protocol which is known as the Cluster Agent Protocol v1 or CAPv1. The CAP is designed to support multi-cluster communication from a single agent, but the current Kubernaut Agent does not support multiple cluster registration and heartbeating.

# Cluster Identifier

Establishing cluster identity in Kubernetes is difficult because there is no official mechanism to find a unique and deterministic cluster identifier built into Kubernetes. Until such a feature exists, the Kubernaut agent relies on the `UID` of the `default` namespace in Kubernetes. The `default` namespace is special in that it cannot be deleted. Therefore, two clusters are distinct from the view of the controller if the `UID` of the `default` namespace in each cluster is unique.

# Agent Identifier 

Each agent has a unique identifier. The ID is a UUID and it stored in `$HOME/.config/kubernaut-agent/id`. When the agent starts the `id` file is read but if the `id` file does not exist or is empty then it is created and populated.

The agent identifier exists primarily to allow the controller to associate one or more clusters to an agent and if the agent disconnects when the agent reconnects the controller can sync any change of state to the agent which can then take appropriate action on its clusters.

The agent identifier is sent as the `agent-id` query parameter in the websocket endpoint URL. 

# Startup Process

When the agent starts the following things occur:

1. The agent ID is read or created.
2. A web socket connection is opened with the Controller.
3. The agent sends a `agent-sync-request` message to the Controller.

    ```json
    {
      "@type": "agent-sync-request"
    }
    ```

4. The server responds with a `agent-sync-response` message to agent. The response message will contain information, if any exists, about the status of a claim associated with a cluster. If the controller is not aware of any clusters associated with an agent then the `clusters` object is empty.

    ```json
    {
      "@type": "agent-sync-response",
      "clusters": {
        "__CLUSTER_ID__": {"status": "UNCLAIMED|CLAIMED|DISCARDED"}
      }
    }
    ```

# Cluster Registration and Handshake

If the `agent-sync-response` message is empty then the agent can send one or more clusters to the controller for registration:

```json
    {
      "@type": "cluster-registration-request",
      "clusters": {
        "__CLUSTER_ID__": {"group": "_POOL_NAME_", "kubeconfig": "__KUBECONFIG__"}
      }
    }
```

The controller sends back a response for each attempted registration:

```json
    {
      "@type": "cluster-registration-response",
      "clusters": {
        "__CLUSTER_ID__": {"status": "ACCEPTED|REJECTED"}
      }
    }
```

For each `ACCEPTED` registration the agent needs to send periodic heartbeats to the controller to indicate the clusters are still available to be claimed. The heartbeat is just a list of cluster identifiers that on the controller side cause an expiration TTL to be extended into the future.

```json
    {
      "@type": "cluster-heartbeat",
      "clusters": ["__CLUSTER_ID__"]
    }
```

# Disconnect and Reconnect

If the agent disconnects then the controller purges from storage any references to an UNCLAIMED cluster associated with the agent. When and if the agent reconnects, then the controller will send claim status information to the agent.











    
