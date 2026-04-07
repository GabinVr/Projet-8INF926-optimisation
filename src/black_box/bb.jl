#!/usr/bin/env julia

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


##### Above is stolen from partie2.jl
##### Below is new


function evaluate_blackbox(Q_turbines, Qtotal, h_amont)
    sum_Q = sum(Q_turbines)
    
    constraint_sum = sum_Q - Qtotal
    h_aval = calc_h_aval(Qtotal)
    
    total_power = 0.0
    
    for i in 1:5
        Q_i = Q_turbines[i]
        if Q_i > 0.0
            head = h_net(h_amont, h_aval, Q_i)
            power_i = power_turbine(Q_i, head, i)
            
            # If power is negative, then bad
            if power_i < 0.0
              return 1e20, 1e10
            end
            
            total_power += power_i
        end
    end
    
    # Apparently NOMAD only minimizes, so we set this as negative
    return -total_power, constraint_sum
end



function main()
    if length(ARGS) != 1
        error("Usage: julia turbine_bb.jl <input_file>")
    end
    
    input_file = ARGS[1]
    
    variables = Float64[]
    open(input_file, "r") do f
        line = readline(f)
        for val_str in split(line)
            val_str = strip(val_str)
            if !isempty(val_str)
                push!(variables, parse(Float64, val_str))
            end
        end
    end
    
    if length(variables) != 7
        error("Attendu 7 variables, reçu $(length(variables))")
    end
    
    Q1 = variables[1]
    Q2 = variables[2]
    Q3 = variables[3]
    Q4 = variables[4]
    Q5 = variables[5]
    Qtotal = variables[6]
    h_amont = variables[7]
    
    obj, constraint = evaluate_blackbox([Q1, Q2, Q3, Q4, Q5], Qtotal, h_amont)
    
    println("$obj $constraint")
end

main()
