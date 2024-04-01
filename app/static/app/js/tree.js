

/**
 * Creates a list of task trees from a flat array of tasks (as stored in the DB). Each task is transformed into a node
 * with a name and ID, and nodes are nested within their parent tasks to form a tree structure.
 * Source: ChatGPT
 * 
 * @param {Object[]} tasks - An array of task objects to be transformed into a tree.
 * Each task object must have at least an id, name, and parentTaskID property. Root(s) can have a parent ID of none.
 * 
 * @returns {Object} The list of root nodes of the task tree, with nested children representing
 * the hierarchical structure of tasks. Each node in the tree will have a name, id,
 * and a children array.
 * 
 */


function createTaskTrees(tasks) {
    const taskMap = {};
    const roots = [];

    // Step 1: Create a map of all tasks by their ID
    tasks.forEach(task => {
        taskMap[task.id] = { ...task, children: [] };
    });

    // Step 2: Build the trees by assigning children to their parents
    tasks.forEach(task => {
        if (task.parentTaskID === null) {
            // If there is no parentTaskID, this is a root node
            roots.push(taskMap[task.id]);
        } else {
            // If there is a parentTaskID, add this task to its parent's children array
            if (taskMap[task.parentTaskID]) {
                taskMap[task.parentTaskID].children.push(taskMap[task.id]);
            }
        }
    });

    // Step 3: Convert each tree to the desired format (name instead of id)
    const convertToNameFormat = (node) => {
        const newNode = { name: node.name, id: node.id, status: node.status, children: [] };
        if (node.children.length) {
            newNode.children = node.children.map(convertToNameFormat);
        }
        return newNode;
    };

    return roots.map(root => convertToNameFormat(root));
}


/**
 * Creates a tree visualization using D3.js. Source: https://observablehq.com/@d3/tree
 * 
 * @param {Object} data - The data for the tree structure. Need to be in the structure shown here: https://observablehq.com/@d3/tree
 * @param {Object} [options] - Configuration options for the tree visualization.
 * @param {Function} [options.label] - A function that, given a node d, returns the display name for that node.
 * @param {Function} [options.link] - A function that, given a node d, returns its link (if any).
 * @param {Function} [options.createTaskLink] - A function that, given a node d, returns its link to create a child task
 * @param {Function} [options.fill] - A function that, given a node d, returns its fill color
 * @param {number} [options.width=200] - The outer width of the tree, in pixels.
 * @param {number} [options.height=200] - The outer height of the tree, in pixels.
 * @returns {Object} The SVG node representing the tree visualization.
 * 
 */
function Tree(data, {
    label, // given a node d, returns the display name
    link, // given a node d, its link (if any)
    createTaskLink,
    fill, // given a node d, its color (if any)
    width = 200, // outer width, in pixels
} = {}) {
    
    let tree = d3.tree // layout algorithm
    let stroke = "#FFFFFF" // stroke for links
    let strokeWidth = 2 // stroke width for links
    let strokeOpacity = 0.4 // stroke opacity for links
    let curve = d3.curveBumpX // curve for the link
    const nodeWidth = 150 //Pixels
    const nodeHeight = 50;  // Pixels
    const maxTextLength = 18
    


    const root = d3.hierarchy(data);

    // Compute labels
    const descendants = root.descendants();
    const L = label == null ? null : descendants.map(d => label(d.data, d));
    //const node_fill = fill == null ? null : descendants.map(d => fill(d.data, d));

    // Compute the layout.
    const dx = 60; // vertical distance
    //const dy = width / (root.height + padding);
    const dy = 200;
    tree().nodeSize([dx, dy])(root);

    // Center the tree.
    let x0 = Infinity;
    let x1 = -x0;
    root.each(d => {
    if (d.x > x1) x1 = d.x;
    if (d.x < x0) x0 = d.x;
    });

    const height = x1 - x0 + dx * 2;

    // Use the required curve
    if (typeof curve !== "function") throw new Error(`Unsupported curve`);
    
    const svg = d3.create("svg")
        //.attr("viewBox", [-dy, -height/2, width, height])
        .attr("viewBox", [-300, x0 - 30, width, height])
        .attr("width", width)
        .attr("height", height)
        .attr("style", "max-width: 100%; max-height: 100%; min-height:100%") // Ensure it doesn't exceed the bounds
        //.attr("style", "max-width: 100%; height:90%;") // Ensure it doesn't exceed the bounds
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("id", "graph-svg")
        .call(d3.zoom()
        .scaleExtent([0.75, 5])
        .on("zoom", (event) => {
            zoomableGroup.attr("transform", event.transform);
        }));


    const zoomableGroup = svg.append("g");

    const lines = zoomableGroup.append("g")
        .attr("fill", "none")
        .attr("stroke", stroke)
        .attr("stroke-opacity", strokeOpacity)
        .attr("stroke-width", strokeWidth)
        .selectAll("path")
        .data(root.links())
        .join("path")
            .attr("d", d3.link(curve)
                .x(d => d.y)
                .y(d => d.x))
  

    const node = zoomableGroup.append("g")
    .selectAll("a")
    .data(root.descendants())
    .join("a")
    .attr("xlink:href", link == null ? null : d => link(d.data, d))
    .attr("transform", d => `translate(${d.y},${d.x})`)
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));






    function dragstarted(event, d) {
        d3.select(this).raise();
        svg.attr("cursor", "grabbing");
    
        // Store the initial position for the drag operation
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        // Calculate the displacement
        let dx = event.x - d.fx;
        let dy = event.y - d.fy;
    
        // Move the node and its descendants
        function move(node) {
            node.x += dy;
            node.y += dx;
            if (node.children) {
                node.children.forEach(move);
            }
        }
    
        move(d);
    
        // Update the node positions and links
        node.attr("transform", d => `translate(${d.y},${d.x})`);
        lines.attr("d", d3.linkHorizontal().x(d => d.y).y(d => d.x));
    }
    
    function dragended(event, d) {
        let newParent = null;
    
        // Define the boundaries of the dragged node
        let draggedNodeBounds = {
            left: d.x - nodeWidth / 2,
            right: d.x + nodeWidth / 2,
            top: d.y - nodeHeight / 2,
            bottom: d.y + nodeHeight / 2
        };
    
        // Check for overlap with other nodes
        node.each(n => {
            if (true) { // n.id !== d.id && n.parent.id !== d.id
                let targetNodeBounds = {
                    left: n.x - nodeWidth / 2,
                    right: n.x + nodeWidth / 2,
                    top: n.y - nodeHeight / 2,
                    bottom: n.y + nodeHeight / 2
                };
    
                // Check if the nodes overlap
                if (draggedNodeBounds.left < targetNodeBounds.right &&
                    draggedNodeBounds.right > targetNodeBounds.left &&
                    draggedNodeBounds.top < targetNodeBounds.bottom &&
                    draggedNodeBounds.bottom > targetNodeBounds.top) {
                    newParent = n;
                }
            }
        });
        
        console.log("HERE")
        if (newParent) {
            console.log("HERE:", newParent)
        }
    
        // Reset the fixed positions
        delete d.fx;
        delete d.fy;
    }
        


    const textGroup = node.append("g")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));


    textGroup.append("rect")
        .attr("fill", d => fill(d.data, d))
        .attr("rx", 5)
        .attr("width",  nodeWidth)// .attr("width",  `${maxTextLength*0.85}em`)
        .attr("height", nodeHeight)
        .attr("y", -nodeHeight / 2)




    // "+"" Icon
    const iconGroup = textGroup.append("g")
                    .attr("transform", `translate(${nodeWidth} 0)`) // Does not allow em as a unit 
    const iconLink = iconGroup.append("a")
                    .attr("xlink:href", createTaskLink == null ? null : d => createTaskLink(d.data, d));
    iconLink.append("circle")
        .attr("fill", "#555555")
        .attr("r", 10)
    iconLink.append("text")
        .attr("dominant-baseline", "middle")
        .attr("text-anchor", "middle")
        .attr("paint-order", "stroke")
        .attr("fill", "white")
        .style("font-size", "14px")
        .text("+")
        

    if (L) {
    text = textGroup.append("text")
        .attr("paint-order", "stroke")
        .attr("fill", "white")
        .style("font-size", "14px");
    
    // Add text, wrapping it to up to 3 lines
    text.each(function(d, i) {
        const MAXLINES = 3;
        let lineIndex = 0
        let lineNumber = 0
        let line = ""

        let words = L[i].split(" ");
        
        for (word of words) {
        // Check if need to move to next line
        if (word.length + lineIndex > maxTextLength) {

            // Last line
            if (lineNumber == MAXLINES - 1) {
            // Replace last 3 characters with ...
            if (lineIndex > maxTextLength - 3) {
                line = line.substring(0, line.length - 3) + '...';
            } else {
                line += '...'
            }
            }

            d3.select(this).append("tspan")
            .attr("x", 5)
            .attr("dy", lineNumber== 0 ? -nodeHeight/6 : "1em") // Move the tspan to the next line if not first line
            .text(line); 

            lineNumber += 1
            lineIndex = 0
            line = ""

            if (lineNumber >= MAXLINES) break
        }

        line += word + " "
        lineIndex += word.length + 1

        }

        // Append Last line if max words not reached
        if (lineNumber < MAXLINES) {
        d3.select(this).append("tspan")
        .attr("x", 5)
        .attr("dy", lineNumber == 0 ? -nodeHeight/6 : "1em") // Move the tspan to the next line if not first line
        .text(line); 
        }

    });
    }

    
    return svg.node();
}