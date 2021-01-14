#version 130 					// required to use OpenGL core standard

// This code was adapted from a tutorial on how to build Fur Effects, written on the website
// xbdev.net. (https://xbdev.net/directx3dx/specialX/Fur/)

//=== in attributes, read from vertex array
in  vec3 position;				// the position of the attribute contains the vertex position
in  vec3 normal;				// store the vertex normal
in  vec2 texCoord;				// texture coordinates
in 	vec3 fur;					// puts the lines on the object

//=== Uniforms
uniform  float furFlowOffset;	// this is for fur animation and movement
uniform  float current_layer;	// current layer
uniform  float num_of_layers;	// number of layers
uniform	 float fur_length;		// fur length

//=== View uniforms
uniform mat4 model;				// model matrix
uniform mat4 view;				// view matrix
uniform mat4 projection;		// projection matrix

//=== Out attributes, interpolated on the face, given to fragment shader
out vec2 frag_TexCoord;	// outputs the texture coordinates

vec4 vGravity = vec4(0.0f, -2.0f, 0.0f, 1.0f);  // gives curves on the end of the fur, like gravity

//=== main shader code
void main(void) {
	// This extrudes the surface to the gap, along the normal.
	// This is the main part, it creates the layers.
	vec3 Pos = position.xyz + (normal * (current_layer * (fur_length / num_of_layers)));
	// This translates the fur strands into the global coordinates
	vec4 P = (model* view * vec4(Pos,1.0));

	// This gives curves to the end of the hair strands, makes it look like gravity affects the strands
	float layer_normalise = (current_layer / num_of_layers);
	// More code to simulate the gravity
	vGravity = (vGravity * model * view);

	// This makes just the tips of the hairs to bend,
	// the layer goes from 0->1 but curves more.
	float k = pow(layer_normalise, 3) * 0.08;
	P = P + vGravity * k;
	// This is the end of the fur gravity stuff

	if(current_layer != 0){
		P = P + vec4(1.0f, 1.0f, 1.0f, 1.0f) * (furFlowOffset);
	}

	frag_TexCoord = texCoord;
    gl_Position = projection * P;
}