

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
 * @param {[Object]} dataList - List of the data for the tree structure. Need to be in the structure shown here: https://observablehq.com/@d3/tree
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
function Trees(dataList, {
    label, // given a node d, returns the display name
    link, // given a node d, its link (if any)
    createTaskLink,
    fill, // given a node d, its color (if any)
    width = 200, // outer width, in pixels
    height = 200
} = {}) {
    
    let tree = d3.tree // layout algorithm
    let stroke = "#FFFFFF" // stroke for links
    let strokeWidth = 2 // stroke width for links
    let strokeOpacity = 0.4 // stroke opacity for links
    let curve = d3.curveBumpX // curve for the link
    const nodeWidth = 150 //Pixels
    const nodeHeight = 50;  // Pixels
    const maxTextLength = 18
    let firstNodeHeight = 0

    let verticalOffset = 0; // Initial vertical-offset at the top of the SVG
    let totalHeight = 0;


    const totalSVG = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .call(d3.zoom()
        .scaleExtent([0.75, 5])
        .on("zoom", (event) => {
            zoomableGroup.attr("transform", event.transform);
        })
    );

    const zoomableGroup = totalSVG.append("g")


    dataList.forEach((data, index) => {
        
        const root = d3.hierarchy(data);

        // Compute labels
        const descendants = root.descendants();
        const L = label == null ? null : descendants.map(d => label(d.data, d));
        //const node_fill = fill == null ? null : descendants.map(d => fill(d.data, d));

        // Compute the layout.
        const dx = 60; // vertical distance
        //const dy = width / (root.height + padding);
        const dy = 200;
        tree()
        .nodeSize([dx, dy])
        .separation(function(a, b) {
          return (a.parent == b.parent ? 1 : 1.5);
        })(root);

        let x0 = Infinity; // Initialize to the largest possible value
        let x1 = -Infinity; // Initialize to the smallest possible value

        root.each(d => {
            console.log("d.x",d.x)
            if (d.x < x0) x0 = d.x; // Find the minimum y-coordinate
            if (d.x > x1) x1 = d.x; // Find the maximum y-coordinate
        });

        //const treeHeight =  (x1 - x0)/2 + nodeHeight ; // This gives you the vertical span of the tree plus buffer.
        const treeHeight =   (x1 - x0) +  dx ; // This gives you the vertical span of the tree plus buffer.
        totalHeight += treeHeight
        if (index == 0) firstNodeHeight = treeHeight

        // Use the required curve
        if (typeof curve !== "function") throw new Error(`Unsupported curve`);
        
        const svg = zoomableGroup.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 10)
            .attr("transform", `translate(0,${verticalOffset})`)
            //.attr("transform", `translate(0,${200*index})`)
            
        
        // Update to position this tree below the last one
        // All graphs are vertically centered at first graph so next graph needs
        // to be translated by half of the first graph + current graph height + buffer
        verticalOffset +=  index > 0 ? treeHeight: treeHeight/2 + 2* dx; 

        const graphGroup = svg.append("g");

        const lines = graphGroup.append("g")
            .attr("fill", "none")
            .attr("stroke", stroke)
            .attr("stroke-opacity", strokeOpacity)
            .attr("stroke-width", strokeWidth)
            .selectAll("path")
            .data(root.links())
            .join("path")
                .attr("d", d3.link(curve)
                    .x(d => d.y)
                    .y(d => d.x));

        const node = graphGroup.append("g")
        .selectAll("a")
        .data(root.descendants())
        .join("a")
        .attr("xlink:href", link == null ? null : d => link(d.data, d))
        .attr("transform", d => `translate(${d.y},${d.x})`);





        node.append("rect")
            .attr("fill", d => fill(d.data, d))
            .attr("rx", 5)
            .attr("width",  nodeWidth)// .attr("width",  `${maxTextLength*0.85}em`)
            .attr("height", nodeHeight)
            .attr("y", -nodeHeight / 2)

        // "+"" Icon
        const iconGroup = node.append("g")
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
        text = node.append("text")
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

        
        
    })
    // Update view box to fit graph
    const viewBoxHorizontalOffset = -30
    const viewBoxVerticalOffset = -firstNodeHeight/2
    const viewBoxHeight = totalHeight * 1.1; // Prevent graph from overflowing
    totalSVG.attr("viewBox", [viewBoxHorizontalOffset, viewBoxVerticalOffset, width, viewBoxHeight]);
    return totalSVG.node();
}