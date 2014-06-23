
local sp = {}

function sp.addAnimFuncs( node )

    local function updateAnim(dt)
        local sequence = node.sequence
        if sequence == nil then
            do return end
        end


        local timer = node.timer + dt
        if timer > sequence.length then
            timer = sequence.length
        end

        for k, v in pairs(sequence.nodes) do
            for action, timeline in pairs(v) do
                local prev, next
                for i, t in ipairs(timeline) do
                    local temp = timeline[i + 1] and timeline[i + 1].time or sequence.length + 1
                    if timer >= t.time and timer < temp then
                        prev, next = t, timeline[i + 1]
                        break
                    end
                end

                if prev then
                    local p = next ~= nil and (timer - prev.time) / (next.time - prev.time) or 0

                    local function calc_with_progress(x1, x2, p)
                        return x1 + (x2 - x1) * p
                    end

                    if action == 'visible' then
                        k:setVisible(prev.value)
                    elseif action == 'position' or action == 'scale' or action == 'skew' then
                        local x1, y1 = prev.value.x, prev.value.y
                        local tx, ty = x1, y1
                        if next then
                            local x2, y2 = next.value.x, next.value.y
                            tx = calc_with_progress(x1, x2, p)
                            ty = calc_with_progress(y1, y2, p) 
                        end

                        if action == 'position' then
                            k:setPosition(cc.p(tx, ty))
                        elseif action == 'scale' then
                            k:setScale(tx, ty)
                        elseif action == 'skew' then
                            k:setSkewX(tx)
                            k:setSkewY(ty)
                        end

                    elseif action == 'rotation' then
                        local r1 = prev.value
                        local r2 = next ~= nil and next.value or r1 
                        k:setRotation(calc_with_progress(r1, r2, p))
                    elseif action == 'opacity' then
                        local o1 = prev.value
                        local o2 = next ~= nil and next.value or o1 
                        k:setOpacity(calc_with_progress(o1, o2, p) * 255)
                    elseif action == 'color' then
                        local r1, g1, b1 = prev.value.r, prev.value.g, prev.value.b
                        local r2, g2, b2 = r1, g1, b1
                        if next then
                            r2 = next.value.r
                            g2 = next.value.g
                            b2 = next.value.b
                        end
                        local r = calc_with_progress(r1, r2, p)
                        local g = calc_with_progress(g1, g2, p)
                        local b = calc_with_progress(b1, b2, p)
                        k:setColor(cc.c3b(r, g, b))
                    elseif action == 'spriteFrame' then
                        k:setTexture(prev.value)
                    end
                end

            end
        end

        for i,v in ipairs(sequence.callbackChannel) do 
            if node.timer < v.time and timer >= v.time then
                if node[v.func] then
                    node[v.func]()
                end
            end
        end

        if timer >= sequence.length and sequence.chainedSequenceId ~= -1 then
            node:resetAnim()
            node.timer = 0
            node.sequence = node.sequences[sequence.chainedSequenceId]
        else
            node.timer = timer
        end
    end


    local function playAnim(self, anim)
        local sequence = nil
        for k,v in pairs(self.sequences) do
            if anim ~= nil then
                if anim == v.name then
                    sequence = v
                    break
                end
            elseif v.autoPlay then
                sequence = v
                break
            end
        end

        if sequence then
            self:resetAnim()

            self.timer = 0
            self.sequence = sequence
        end
    end

    local function resetAnim(self)
        if self.sequence ~= nil then
            for k, v in pairs(self.sequence.nodes) do
                for action, timeline in pairs(v) do
                    local origin = timeline[1]
                    if action == 'visible' then
                        k:setVisible(origin.value)
                    elseif action == 'position' then
                        k:setPosition(cc.p(origin.value.x, origin.value.y))
                    elseif action == 'scale' then
                        k:setScale(origin.value.x, origin.value.y)
                    elseif action == 'skew' then
                        k:setSkewX(origin.value.x)
                        k:setSkewY(origin.value.y)
                    elseif action == 'rotation' then
                        k:setRotation(origin.value)
                    elseif action == 'opacity' then
                        k:setOpacity(origin.value * 255)
                    elseif action == 'color' then
                        k:setColor(cc.c3b(origin.value.r, origin.value.g, origin.value.b))
                    elseif action == 'spriteFrame' then
                        k:setTexture(origin.value)
                    end
                end
            end
        end
    end

    node:scheduleUpdateWithPriorityLua(updateAnim, 0)
    node.playAnim = playAnim
    node.resetAnim = resetAnim
end

function sp.addBasicFuncs( node )
    local function onNodeEvent(event)
        if event == "enter" then
            if node.onEnter then node.onEnter() end
        elseif event == "exit" then
            if node.onExit then node.onExit() end
        elseif event == 'cleanup' then
            if node.onCleanup then node.onCleanup() end
        end
    end

    node:registerScriptHandler(onNodeEvent)
end

return sp
