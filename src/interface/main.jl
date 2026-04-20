#!/usr/bin/env julia

using Printf

function power_turbine(Q, H, turbine_id)
    if Q == 0.0
        return 0.0
    end
    if turbine_id == 1
        return -90.258 + 0.6049 * Q + 3.0334 * H - 0.0029 * Q^2 + 0.0139 * Q * H - 0.0569 * H^2
    elseif turbine_id == 2
        Qn = (Q - 134.2) / 10.39
        Hn = (H - 34.11) / 0.429
        return 41.736 + 3.5717 * Qn + 0.4274 * Hn - 0.2597 * Qn^2 + 0.0525 * Qn * Hn + 0.0044 * Hn^2
    elseif turbine_id == 3
        Qn = (Q - 136.2) / 4.029
        Hn = (H - 34.14) / 0.4976
        return 40.9 + 1.2454 * Qn + 0.5479 * Hn - 0.0659 * Qn^2 - 0.0130 * Qn * Hn +
               0.0035 * Hn^2 - 0.0022 * Qn^3 + 0.0037 * Qn^2 * Hn + 0.0188 * Qn * Hn^2
    elseif turbine_id == 4
        return -74.121 + 0.6572 * Q + 1.7094 * H - 0.0029 * Q^2 + 0.0141 * Q * H - 0.0355 * H^2
    elseif turbine_id == 5
        return -234.15 + 1.9425 * Q + 5.9587 * H - 0.0017 * Q^2 - 0.0341 * Q * H
    else
        error("ID turbine invalide: $turbine_id")
    end
end

function h_net(h_amont, h_aval, Q)
    return (h_amont - h_aval) - (0.5e-5 * Q^2)
end

function calc_h_aval(Qtotal)
    x = (Qtotal - 642.5) / 171.4
    p1 = -0.0419
    p2 = 0.8844
    p3 = 103.89
    return p1 * x^2 + p2 * x + p3
end

function optimize_turbines(Qtotal, h_amont, q_min::Vector{Float64}, q_max::Vector{Float64})
    n_turbines = 5
    delta_q = 5.0
    h_aval = calc_h_aval(Qtotal)

    # Snap min/max to grid
    # q_min_snap: smallest grid multiple >= q_min (or 0 if turbine can be off)
    # A turbine can be either OFF (Q=0) or running within [q_min, q_max]
    q_min_snap = [ceil(q_min[t] / delta_q) * delta_q for t in 1:n_turbines]
    q_max_snap = [floor(q_max[t] / delta_q) * delta_q for t in 1:n_turbines]

    q_target = floor(Int, Qtotal / delta_q) * delta_q
    states = collect(0.0:delta_q:q_target)
    n_states = length(states)

    dp = fill(-Inf, n_states, n_turbines + 1)
    decisions = zeros(Float64, n_states, n_turbines)

    dp[1, n_turbines + 1] = 0.0

    for t in n_turbines:-1:1
        for (i, q) in enumerate(states)
            max_power = -Inf
            best_decision = -1.0  # sentinel: no valid decision found yet

            # Candidate flow values for turbine t:
            # either OFF (0.0) or any grid point in [q_min_snap[t], q_max_snap[t]]
            candidates = Float64[]

            # Turbine OFF
            push!(candidates, 0.0)

            # Turbine ON: flow in [q_min_snap[t], q_max_snap[t]]
            if q_max_snap[t] >= q_min_snap[t]
                for q_turbine in q_min_snap[t]:delta_q:q_max_snap[t]
                    push!(candidates, q_turbine)
                end
            end

            for q_turbine in candidates
                # Cannot assign more flow than available
                if q_turbine > q + 1e-9
                    continue
                end

                remaining_q = q - q_turbine
                j = floor(Int, remaining_q / delta_q) + 1

                if 1 <= j <= n_states && isfinite(dp[j, t + 1])
                    head = h_net(h_amont, h_aval, q_turbine)
                    power = power_turbine(q_turbine, head, t) + dp[j, t + 1]
                    if power > max_power
                        max_power = power
                        best_decision = q_turbine
                    end
                end
            end

            dp[i, t] = max_power
            decisions[i, t] = best_decision == -1.0 ? 0.0 : best_decision
        end
    end

    solution = zeros(Float64, n_turbines)
    remaining = q_target
    for t in 1:n_turbines
        idx = floor(Int, remaining / delta_q) + 1
        q_t = decisions[idx, t]
        solution[t] = q_t
        remaining -= q_t
    end

    return solution, dp[end, 1], q_target
end

function main()
    if length(ARGS) != 12
        println("Usage: script.jl <Q_total> <h_amont> " *
                "<Q_min_T1> <Q_min_T2> <Q_min_T3> <Q_min_T4> <Q_min_T5> " *
                "<Q_max_T1> <Q_max_T2> <Q_max_T3> <Q_max_T4> <Q_max_T5>")
        exit(1)
    end

    q_total = parse(Float64, ARGS[1])
    h_amont = parse(Float64, ARGS[2])

    q_min = [parse(Float64, ARGS[2 + t]) for t in 1:5]
    q_max = [parse(Float64, ARGS[7 + t]) for t in 1:5]
    q_total = min(q_total, sum(q_max))

    # Validate constraints
    for t in 1:5
        if q_min[t] < 0.0
            error("Q_min for turbine $t must be >= 0")
        end
        if q_max[t] < q_min[t]
            error("Q_max for turbine $t must be >= Q_min ($(q_min[t]))")
        end
    end

    h_aval = calc_h_aval(q_total)
    flows, power, q_target = optimize_turbines(q_total, h_amont, q_min, q_max)

    println("Repartition optimale des debits:")
    for (i, q) in enumerate(flows)
        @printf("  Turbine %d: %.1f m3/s\n", i, q)
    end
    @printf("h_aval predit: %.4f m\n", h_aval)
    @printf("Q cible discretise: %.1f m3/s\n", q_target)
    @printf("Puissance totale predite: %.2f MW\n", power)
end

main()
