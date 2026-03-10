local map = {
    ["b522a6bb51a0"] = "fluentbit",
    ["da16de59df94"] = "qdrant",
    ["5922fb64ecf1"] = "loki",
    ["5c8e9b0be855"] = "grafana",
    ["5c27342f7e69"] = "vault",
    ["b496b29f971c"] = "rundeck",
    ["eff2c68f60c4"] = "st2-web",
    ["8505b576559b"] = "st2-client",
    ["4842f3db0aef"] = "st2-workflowengine",
    ["56b2b1b3795f"] = "st2-rulesengine",
    ["b79167533c11"] = "st2-timersengine",
    ["0c08c1735141"] = "st2-notifier",
    ["0256448a99c4"] = "st2-sensorcontainer",
    ["947f6ddb92d1"] = "st2-scheduler",
    ["9c19e2b9dda6"] = "st2-actionrunner",
    ["a99844bb561f"] = "st2-auth",
    ["6fbfa049c268"] = "st2-garbagecollector",
    ["5b8cd9625ddf"] = "st2-stream",
    ["8db161322f7e"] = "st2-api",
    ["0b07d6ecc25e"] = "redis",
    ["9e86f73ed8b5"] = "rabbitmq",
    ["05c5e73bfc11"] = "mongo",
    ["7cd960155ce0"] = "awx",
}

function add_container_name(tag, timestamp, record)
    local id = string.match(tag, "docker%.(.+)")
    if id then
        local short = string.sub(id, 1, 12)
        record["container_name"] = map[short] or short
    end
    return 1, timestamp, record
end
