fetch(`http://127.0.0.1:8000/?userID=${session.userId}`, {
    method: 'GET'
  }).then(async (response) => {
    const body = await response.json()
    if (!response.ok) {
      console.error(body.message)
    } else {
      setProjectsDiv(
        <div>
          <ul>
            {body.projects.map((project, index) => (
              <li key={index} className=' font-light '>
                <Link href={`/${project._id}`}><Button label={project.name} className='w-32 mx-4' /></Link>
              </li>
            ))}
          </ul>
        </div>
      )
    }
  }).catch(error => {
    console.error('Left sidebar Project warning:', error)
  })